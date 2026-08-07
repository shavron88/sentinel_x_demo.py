import sys
import os
import time
from typing import Optional, List, Dict, Any

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


class YOLOInferenceEngine:
    def __init__(self, model_path: str = "yolov8n.pt", health_monitor=None):
        self.model_path = model_path
        self.health_monitor = health_monitor
        self.model = None
        self._init_model()

    def _init_model(self):
        if YOLO_AVAILABLE:
            try:
                self.model = YOLO(self.model_path)
                if self.health_monitor:
                    self.health_monitor.update_yolo_status("Loaded")
            except Exception as e:
                if self.health_monitor:
                    self.health_monitor.update_yolo_status(f"Error: {e}")
        else:
            if self.health_monitor:
                self.health_monitor.update_yolo_status("Mock Mode (Ultralytics missing)")

    def infer_frame(self, frame: Any) -> List[Dict[str, Any]]:
        """Frame par detection chalata hai aur results return karta hai."""
        start_time = time.time()
        results = []

        if self.model and not isinstance(frame, str):
            res = self.model(frame, verbose=False)
            for r in res:
                for box in r.boxes:
                    results.append({
                        "bbox": [round(x, 2) for x in box.xyxy[0].tolist()],
                        "confidence": round(float(box.conf[0]), 2),
                        "class_id": int(box.cls[0]),
                        "label": self.model.names[int(box.cls[0])]
                    })
        else:
            # Fallback mock detection testing ke liye
            time.sleep(0.02)  # 20ms simulated latency
            results.append({
                "bbox": [100.0, 150.0, 250.0, 400.0],
                "confidence": 0.92,
                "class_id": 0,
                "label": "person"
            })

        duration = time.time() - start_time
        if self.health_monitor:
            self.health_monitor.record_inference(duration)

        return results


if __name__ == "__main__":
    # Root folder ko python path me add karta hai taaki imports fail na ho
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from ai.health import AIHealthMonitor

    health = AIHealthMonitor()
    engine = YOLOInferenceEngine(health_monitor=health)

    print("--- Testing YOLO Inference Engine ---")
    mock_frame = "dummy_image_matrix"
    detections = engine.infer_frame(mock_frame)
    print(f"Detections Output: {detections}")
    print(f"Health Status: {health.get_health_status()['yolo_status']}")
    print(f"Inference Time: {health.get_health_status()['metrics']['last_inference_ms']} ms")