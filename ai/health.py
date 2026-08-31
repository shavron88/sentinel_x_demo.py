import time
from typing import Dict, Any


class AIHealthMonitor:
    def __init__(self):
        self.yolo_status = "Uninitialized"
        self.tracker_status = "Idle"
        self.pipeline_status = "Stopped"
        self.recovery_status = "Normal"

        self.frame_count = 0
        self.inference_count = 0
        self._fps_start = time.time()
        self.current_fps = 0.0
        self.last_inference_ms = 0.0
        self.avg_inference_ms = 0.0
        self.total_inference_time = 0.0

        self.queue_size = 0
        self.max_queue_size = 100

    def update_yolo_status(self, status: str):
        self.yolo_status = status
        self._update_pipeline_status()

    def update_tracker_status(self, status: str):
        self.tracker_status = status
        self._update_pipeline_status()

    def _update_pipeline_status(self):
        yolo_ok = self.yolo_status in ["Loaded", "Running"]
        tracker_ok = self.tracker_status in ["Active", "Running"]

        if yolo_ok and tracker_ok and self.recovery_status == "Normal":
            self.pipeline_status = "Healthy"
        elif yolo_ok or tracker_ok:
            self.pipeline_status = "Degraded"
        else:
            self.pipeline_status = "Stopped"

    def update_queue_size(self, size: int):
        self.queue_size = size

    def record_inference(self, duration_seconds: float):
        duration_ms = duration_seconds * 1000
        self.frame_count += 1
        self.inference_count += 1
        self.last_inference_ms = round(duration_ms, 2)
        self.total_inference_time += duration_ms
        self.avg_inference_ms = round(self.total_inference_time / self.inference_count, 2)

        elapsed = time.time() - self._fps_start
        if elapsed >= 1.0:
            self.current_fps = round(self.frame_count / elapsed, 2)
            self.frame_count = 0
            self._fps_start = time.time()

    def set_recovery(self, is_recovering: bool):
        self.recovery_status = "Recovering" if is_recovering else "Normal"
        self._update_pipeline_status()

    def get_health_status(self) -> Dict[str, Any]:
        is_healthy = (
            self.yolo_status in ["Loaded", "Running"]
            and self.tracker_status in ["Active", "Running"]
            and self.recovery_status == "Normal"
            and self.queue_size < (self.max_queue_size * 0.9)
        )

        return {
            "timestamp": time.time(),
            "status": "Healthy" if is_healthy else "Degraded",
            "pipeline_status": self.pipeline_status,
            "yolo_status": self.yolo_status,
            "tracker_status": self.tracker_status,
            "recovery_status": self.recovery_status,
            "metrics": {
                "detection_fps": self.current_fps,
                "last_inference_ms": self.last_inference_ms,
                "avg_inference_ms": self.avg_inference_ms,
                "queue_size": self.queue_size,
                "queue_capacity_percent": round((self.queue_size / self.max_queue_size) * 100, 1)
            }
        }


if __name__ == "__main__":
    import json

    ai_health = AIHealthMonitor()
    ai_health.update_yolo_status("Loaded")
    ai_health.update_tracker_status("Active")

    for _ in range(5):
        time.sleep(0.03)
        ai_health.record_inference(0.03)

    print("--- AI Health Monitoring Stats ---")
    print(json.dumps(ai_health.get_health_status(), indent=4))
