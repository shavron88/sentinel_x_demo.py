import sys
import os
import time
import logging
from typing import Optional, List, Dict, Any
from collections import Counter

import torch

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

from config import (
    MODEL_PATH,
    CONFIDENCE_THRESHOLD,
    IOU_THRESHOLD,
    IMAGE_SIZE,
    DEVICE,
    TARGET_CLASSES,
    TRACKING_ENABLED,
    TRACKER,
)

logger = logging.getLogger("SentinelX.Inference")

# COCO class IDs relevant to surveillance. Used as a fallback when the
# TARGET_CLASSES config resolves to an empty list.
_DEFAULT_CLASSES = [0, 1, 2, 3, 5, 7, 24, 26, 28]

# Rate-limit the per-frame detection summary log so the terminal is not spammed.
_LOG_SUMMARY_INTERVAL = 5.0


class YOLOInferenceEngine:
    """YOLO11 detection + tracking inference engine.

    Clean interface (consumed by the Sentinel-X worker/engine):
        load_model() -> bool
        detect(frame) -> list[dict]
        track(frame) -> list[dict]
        get_detections() -> list[dict]
        release()

    The legacy ``infer_frame(frame, frame_id=None)`` entry point is preserved
    for backward compatibility with the existing YOLOWorker / recovery pipeline
    so the rest of Sentinel-X is unaware of the underlying model version.
    """

    def __init__(
        self,
        model_path: str = None,
        health_monitor=None,
        camera_id: str = None,
        conf: float = None,
        iou: float = None,
        imgsz: int = None,
        device: str = None,
        classes: Optional[List[int]] = None,
        tracking: Optional[bool] = None,
        tracker: str = None,
    ):
        if model_path is None:
            model_path = MODEL_PATH
        self.model_path = model_path
        self.health_monitor = health_monitor
        self.camera_id = camera_id
        self.conf = CONFIDENCE_THRESHOLD if conf is None else conf
        self.iou = IOU_THRESHOLD if iou is None else iou
        self.imgsz = IMAGE_SIZE if imgsz is None else imgsz
        self.device = DEVICE if device is None else device
        self.classes = TARGET_CLASSES if classes is None else (classes or _DEFAULT_CLASSES)
        self.tracking = TRACKING_ENABLED if tracking is None else tracking
        self.tracker = TRACKER if tracker is None else tracker

        self.model = None
        self.model_name = None
        self.model_version = None
        self.resolved_device = None

        # Last-set state (returned by get_detections)
        self._last_detections: List[Dict[str, Any]] = []
        self._last_timestamp: float = 0.0

        # Rate-limiting for summary logging
        self._last_summary_log: float = 0.0

        self._init_model()

    # ==================================================================
    # Device resolution
    # ==================================================================
    def _resolve_device(self) -> str:
        """Resolve the inference device, gracefully falling back to CPU."""
        if self.device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        if self.device == "cuda":
            if not torch.cuda.is_available():
                logger.warning("CUDA requested but not available; falling back to CPU.")
                return "cpu"
            return "cuda"
        return self.device

    # ==================================================================
    # Model lifecycle
    # ==================================================================
    def _init_model(self):
        """Load the YOLO11 model from disk with graceful failure handling."""
        if not YOLO_AVAILABLE:
            logger.error("Ultralytics is not installed -- YOLO11 unavailable")
            if self.health_monitor:
                self.health_monitor.update_yolo_status("Unavailable (Ultralytics missing)")
                self.health_monitor.update_tracker_status("Error")
            return

        if not self.model_path or not os.path.isfile(self.model_path):
            logger.error(f"Model file not found: {self.model_path}")
            if self.health_monitor:
                self.health_monitor.update_yolo_status(f"Error: Model file not found: {self.model_path}")
                self.health_monitor.update_tracker_status("Error")
            return

        try:
            logger.info(f"Loading YOLO11 model from: {self.model_path}")
            self.resolved_device = self._resolve_device()
            self.model = YOLO(self.model_path)

            # Move the wrapped model to the target device (no per-call overhead).
            try:
                self.model.to(self.resolved_device)
            except Exception as dev_err:
                logger.warning(f"Could not move model to '{self.resolved_device}': {dev_err}; using default.")

            self.model_name = os.path.basename(self.model_path)
            # Detect architecture version from the model yaml when available.
            self.model_version = None
            try:
                cfg = getattr(self.model, "model", None)
                if cfg is not None:
                    y = getattr(cfg, "yaml", None)
                    if isinstance(y, dict):
                        # yaml_file e.g. "yolo11n.yaml" confirms the YOLO11 family
                        self.model_version = y.get("yaml_file") or y.get("model")
            except Exception:
                self.model_version = None

            logger.info(
                f"YOLO11 model loaded successfully "
                f"(model={self.model_name}, task={getattr(self.model, 'task', 'detect')}, "
                f"version={self.model_version or 'unknown'}, device={self.resolved_device}, "
                f"imgsz={self.imgsz}, conf={self.conf}, iou={self.iou}, "
                f"classes={self.classes}, tracking={self.tracking})"
            )
            if self.health_monitor:
                self.health_monitor.update_yolo_status("Loaded")
                self.health_monitor.update_tracker_status("Active")
        except Exception as e:
            logger.error(f"Failed to load YOLO11 model '{self.model_path}': {e}", exc_info=True)
            if self.health_monitor:
                self.health_monitor.update_yolo_status(f"Error: {e}")
                self.health_monitor.update_tracker_status("Error")
            self.model = None
            self.resolved_device = None

    def load_model(self) -> bool:
        """(Re)load the model. Returns True on success."""
        self._init_model()
        return self.model is not None

    # ==================================================================
    # Result parsing
    # ==================================================================
    def _parse_results(self, res, frame, timestamp: float) -> List[Dict[str, Any]]:
        """Extract normalized detection dicts from ultralytics Results.

        Preserves the field names consumed by the rest of Sentinel-X:
        track_id, class_id, label, confidence, bbox.
        Adds center point and detection timestamp for richer downstream use.
        """
        detections: List[Dict[str, Any]] = []

        if res is None:
            return detections

        r = res[0] if isinstance(res, (list, tuple)) else res
        if r is None or getattr(r, "boxes", None) is None or len(r.boxes) == 0:
            return detections

        names = r.names
        try:
            h, w = frame.shape[:2]
        except Exception:
            h, w = 1, 1

        for box in r.boxes:
            cls_id = int(box.cls[0])
            conf = round(float(box.conf[0]), 2)
            xyxy = box.xyxy[0].tolist() if box.xyxy is not None else [0, 0, 0, 0]
            x1, y1, x2, y2 = (round(v, 2) for v in xyxy)
            cx = round((x1 + x2) / 2, 2)
            cy = round((y1 + y2) / 2, 2)
            track_id = int(box.id[0]) if box.id is not None and len(box.id) > 0 else None

            detections.append({
                "track_id": track_id,
                "class_id": cls_id,
                "label": names.get(cls_id, str(cls_id)) if isinstance(names, dict) else str(cls_id),
                "confidence": conf,
                "bbox": [x1, y1, x2, y2],
                "center": [cx, cy],
                "width": round(x2 - x1, 2),
                "height": round(y2 - y1, 2),
                "timestamp": round(timestamp, 3),
                "camera_id": self.camera_id,
            })

        return detections

    # ==================================================================
    # Core inference methods
    # ==================================================================
    def detect(self, frame) -> List[Dict[str, Any]]:
        """Run detection-only inference (no tracking). Returns detection list."""
        if not self.model or frame is None or isinstance(frame, str):
            return []
        try:
            res = self.model.predict(
                frame,
                conf=self.conf,
                iou=self.iou,
                classes=self.classes,
                imgsz=self.imgsz,
                verbose=False,
            )
            detections = self._parse_results(res, frame, time.time())
            self._last_detections = detections
            self._last_timestamp = time.time()
            self._log_summary(detections)
            return detections
        except Exception as e:
            logger.error(f"YOLO11 detect() failed: {e}", exc_info=True)
            if self.health_monitor:
                self.health_monitor.update_yolo_status(f"Error: {e}")
            return []

    def track(self, frame) -> List[Dict[str, Any]]:
        """Run detection + ByteTrack inference. Returns detection list."""
        if not self.model or frame is None or isinstance(frame, str):
            return []
        try:
            res = self.model.track(
                frame,
                conf=self.conf,
                iou=self.iou,
                classes=self.classes,
                imgsz=self.imgsz,
                persist=True,
                tracker=self.tracker,
                verbose=False,
            )
            self._last_results = res
            detections = self._parse_results(res, frame, time.time())
            self._last_detections = detections
            self._last_timestamp = time.time()
            self._log_summary(detections)
            return detections
        except Exception as e:
            logger.error(f"YOLO11 track() failed: {e}", exc_info=True)
            if self.health_monitor:
                self.health_monitor.update_yolo_status(f"Error: {e}")
                self.health_monitor.update_tracker_status("Error")
            return []

    def _log_summary(self, detections: List[Dict[str, Any]]):
        """Emit a concise, rate-limited detection summary log."""
        now = time.time()
        if now - self._last_summary_log < _LOG_SUMMARY_INTERVAL:
            return
        if not detections:
            return
        counts = Counter(d["label"] for d in detections)
        logger.info(f"Detections: {dict(counts)} (device={self.resolved_device}, conf={self.conf})")

    def get_detections(self) -> List[Dict[str, Any]]:
        """Return the detections from the most recent inference call."""
        return list(self._last_detections)

    def release(self):
        """Release model resources."""
        try:
            if self.model is not None:
                del self.model
        except Exception:
            pass
        self.model = None
        self._last_detections = []
        self._last_timestamp = 0.0
        if self.health_monitor:
            self.health_monitor.update_yolo_status("Released")
            self.health_monitor.update_tracker_status("Stopped")

    # ==================================================================
    # Backward-compatible entry point used by YOLOWorker / recovery engine
    # ==================================================================
    def infer_frame(self, frame: Any, frame_id: Optional[int] = None) -> Dict[str, Any]:
        """Run inference on a single frame.

        Preserves the legacy return contract consumed by ``ai.worker.YOLOWorker``
        and ``core.engine``: a dict with frame_id, timestamp, detections,
        annotated_frame and error.
        """
        start_time = time.time()
        timestamp = time.time()

        result: Dict[str, Any] = {
            "frame_id": frame_id,
            "timestamp": timestamp,
            "detections": [],
            "annotated_frame": None,
            "error": None,
        }

        if not self.model:
            result["error"] = "Model not initialized"
            if self.health_monitor:
                self.health_monitor.record_inference(time.time() - start_time)
                self.health_monitor.update_yolo_status("Error")
                self.health_monitor.update_tracker_status("Error")
            return result

        if isinstance(frame, str) or frame is None:
            result["error"] = "Invalid frame (string or None)"
            if self.health_monitor:
                self.health_monitor.record_inference(time.time() - start_time)
            return result

        try:
            if self.tracking:
                res = self.model.track(
                    frame,
                    conf=self.conf,
                    iou=self.iou,
                    classes=self.classes,
                    imgsz=self.imgsz,
                    persist=True,
                    tracker=self.tracker,
                    verbose=False,
                )
            else:
                res = self.model.predict(
                    frame,
                    conf=self.conf,
                    iou=self.iou,
                    classes=self.classes,
                    imgsz=self.imgsz,
                    verbose=False,
                )

            detections = self._parse_results(res, frame, timestamp)
            result["detections"] = detections
            self._last_detections = detections
            self._last_timestamp = timestamp

            annotated = None
            try:
                if res and len(res) > 0:
                    annotated = res[0].plot()
            except Exception as plot_err:
                logger.warning(f"YOLO11 plotting failed: {plot_err}")
            if annotated is None:
                annotated = frame.copy()
            result["annotated_frame"] = annotated

            self._log_summary(detections)

            if self.health_monitor:
                self.health_monitor.update_yolo_status("Running")
                self.health_monitor.update_tracker_status("Active")

        except Exception as e:
            logger.error(f"YOLO11 infer_frame() failed: {e}", exc_info=True)
            if self.health_monitor:
                self.health_monitor.update_yolo_status(f"Error: {e}")
                self.health_monitor.update_tracker_status("Error")
            result["error"] = str(e)

        duration = time.time() - start_time
        if self.health_monitor:
            self.health_monitor.record_inference(duration)

        return result


if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from ai.health import AIHealthMonitor

    health = AIHealthMonitor()
    engine = YOLOInferenceEngine(health_monitor=health)

    print("--- Testing YOLO11 Inference Engine ---")
    import numpy as np
    mock_frame = np.zeros((640, 360, 3), dtype=np.uint8)
    result = engine.infer_frame(mock_frame)
    print(f"Model: {engine.model_name}")
    print(f"Device: {engine.resolved_device}")
    print(f"Detections: {len(result['detections'])}")
    print(f"Error: {result['error']}")
    print(f"Health Status: {health.get_health_status()['yolo_status']}")
    print(f"Tracker Status: {health.get_health_status()['tracker_status']}")
    print(f"Pipeline Status: {health.get_health_status()['pipeline_status']}")
    print(f"Inference Time: {health.get_health_status()['metrics']['last_inference_ms']} ms")
    engine.release()
