import sys
import os
import threading
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.queue_manager import DetectionQueueManager
from ai.inference import YOLOInferenceEngine
from ai.health import AIHealthMonitor


class YOLOWorker(threading.Thread):
    def __init__(self, queue_manager: DetectionQueueManager, engine: YOLOInferenceEngine, health_monitor: AIHealthMonitor, on_result=None):
        super().__init__(daemon=True)
        self.queue_manager = queue_manager
        self.engine = engine
        self.health_monitor = health_monitor
        self.on_result = on_result
        self.is_running = False

    def run(self):
        self.is_running = True
        if self.health_monitor:
            self.health_monitor.update_tracker_status("Active")

        while self.is_running:
            item = self.queue_manager.get_frame(timeout=0.1)

            if item is None:
                continue

            frame_id, frame_data = item

            if self.health_monitor:
                self.health_monitor.update_queue_size(self.queue_manager.qsize())

            result = self.engine.infer_frame(frame_data, frame_id=frame_id)
            detections = result.get("detections", [])
            annotated_frame = result.get("annotated_frame")

            if self.on_result:
                self.on_result(frame_id, detections, frame_data, annotated_frame)

            self.queue_manager.push_result(frame_id, detections)

    def stop(self):
        self.is_running = False
        if self.health_monitor:
            self.health_monitor.update_tracker_status("Stopped")


if __name__ == "__main__":
    health = AIHealthMonitor()
    queue_mgr = DetectionQueueManager(maxsize=10)
    engine = YOLOInferenceEngine(health_monitor=health)

    worker = YOLOWorker(queue_manager=queue_mgr, engine=engine, health_monitor=health)

    print("--- Testing YOLO Worker Loop ---")
    worker.start()

    for i in range(1, 4):
        queue_mgr.push_frame(i, f"Frame_{i}_Data")
        time.sleep(0.05)

        res = queue_mgr.get_result()
        if res:
            f_id, det = res
            print(f"Processed Frame {f_id} -> Detections: {len(det)}")

    worker.stop()
    worker.join(timeout=1.0)
    print("Worker stopped successfully.")
