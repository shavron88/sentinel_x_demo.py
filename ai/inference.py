import sys
import os
import time
import logging
from typing import Optional, List, Dict, Any

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

logger = logging.getLogger("SentinelX.Inference")


class YOLOInferenceEngine:
    def __init__(self, model_path: str = None, health_monitor=None):
        if model_path is None:
            from config import MODEL_PATH
            model_path = MODEL_PATH
        self.model_path = model_path
        self.health_monitor = health_monitor
        self.model = None
        self._init_model()

    def _init_model(self):
        if YOLO_AVAILABLE:
            try:
                if not os.path.isfile(self.model_path):
                    logger.error(f"Model file not found: {self.model_path}")
                    if self.health_monitor:
                        self.health_monitor.update_yolo_status(f"Error: Model file not found: {self.model_path}")
                        self.health_monitor.update_tracker_status("Error")
                    return
                logger.info(f"Loading YOLO model from: {self.model_path}")
                self.model = YOLO(self.model_path)
                logger.info(f"YOLO model loaded successfully ({os.path.basename(self.model_path)})")
                if self.health_monitor:
                    self.health_monitor.update_yolo_status("Loaded")
                    self.health_monitor.update_tracker_status("Active")
            except Exception as e:
                logger.error(f"Failed to load YOLO model: {e}", exc_info=True)
                if self.health_monitor:
                    self.health_monitor.update_yolo_status(f"Error: {e}")
                    self.health_monitor.update_tracker_status("Error")
        else:
            logger.error("Ultralytics is not installed — YOLO unavailable")
            if self.health_monitor:
                self.health_monitor.update_yolo_status("Unavailable (Ultralytics missing)")
                self.health_monitor.update_tracker_status("Error")

    def infer_frame(self, frame: Any, frame_id: Optional[int] = None) -> Dict[str, Any]:
        start_time = time.time()

        result = {
            "frame_id": frame_id,
            "timestamp": time.time(),
            "detections": [],
            "annotated_frame": None,
            "error": None
        }

        if not self.model or isinstance(frame, str):
            duration = time.time() - start_time
            if self.health_monitor:
                self.health_monitor.record_inference(duration)
            if not self.model:
                result["error"] = "Model not initialized"
                if self.health_monitor:
                    self.health_monitor.update_yolo_status("Error")
                    self.health_monitor.update_tracker_status("Error")
            return result

        try:
            res = self.model.track(
                frame,
                persist=True,
                tracker="bytetrack.yaml",
                verbose=False
            )

            detections = []
            for r in res:
                if r.boxes is None:
                    continue

                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    track_id = int(box.id[0]) if box.id is not None and len(box.id) > 0 else None
                    bbox = [round(x, 2) for x in box.xyxy[0].tolist()]

                    detections.append({
                        "track_id": track_id,
                        "class_id": cls_id,
                        "label": r.names[cls_id],
                        "confidence": round(float(box.conf[0]), 2),
                        "bbox": bbox
                    })

            result["detections"] = detections
            result["annotated_frame"] = res[0].plot() if res else frame.copy()

            if self.health_monitor:
                self.health_monitor.update_yolo_status("Running")
                self.health_monitor.update_tracker_status("Active")

        except Exception as e:
            duration = time.time() - start_time
            if self.health_monitor:
                self.health_monitor.record_inference(duration)
                self.health_monitor.update_yolo_status(f"Error: {e}")
                self.health_monitor.update_tracker_status("Error")
            result["error"] = str(e)
            return result

        duration = time.time() - start_time
        if self.health_monitor:
            self.health_monitor.record_inference(duration)

        return result


if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from ai.health import AIHealthMonitor

    health = AIHealthMonitor()
    engine = YOLOInferenceEngine(health_monitor=health)

    print("--- Testing YOLO Inference Engine ---")
    import numpy as np
    mock_frame = np.zeros((640, 360, 3), dtype=np.uint8)
    result = engine.infer_frame(mock_frame)
    print(f"Frame ID: {result['frame_id']}")
    print(f"Detections: {len(result['detections'])}")
    print(f"Error: {result['error']}")
    print(f"Health Status: {health.get_health_status()['yolo_status']}")
    print(f"Tracker Status: {health.get_health_status()['tracker_status']}")
    print(f"Pipeline Status: {health.get_health_status()['pipeline_status']}")
    print(f"Inference Time: {health.get_health_status()['metrics']['last_inference_ms']} ms")
