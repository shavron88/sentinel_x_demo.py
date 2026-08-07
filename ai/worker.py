import sys
import os
import threading
import time

# Ensure root import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.queue_manager import DetectionQueueManager
from ai.inference import YOLOInferenceEngine
from ai.health import AIHealthMonitor


class YOLOWorker(threading.Thread):
    def __init__(self, queue_manager: DetectionQueueManager, engine: YOLOInferenceEngine, health_monitor: AIHealthMonitor):
        super().__init__(daemon=True)
        self.queue_manager = queue_manager
        self.engine = engine
        self.health_monitor = health_monitor
        self.is_running = False

    def run(self):
        self.is_running = True
        if self.health_monitor:
            self.health_monitor.update_tracker_status("Active")

        while self.is_running:
            # Queue se frame pull karein
            item = self.queue_manager.get_frame(timeout=0.1)
            
            if item is None:
                continue

            frame_id, frame_data = item
            
            # Health monitor me queue size update karein
            if self.health_monitor:
                self.health_monitor.update_queue_size(self.queue_manager.qsize())

            # Inference chalayein
            detections = self.engine.infer_frame(frame_data)

            # Processed result output queue me bhejein
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

    # Worker me frames push karke check karte hain
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