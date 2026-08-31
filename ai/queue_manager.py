import queue
import threading
import time
from typing import Optional, Any, Tuple

class DetectionQueueManager:
    def __init__(self, maxsize: int = 30):
        self.maxsize = maxsize
        self.frame_queue = queue.Queue(maxsize=maxsize)
        self.result_queue = queue.Queue(maxsize=maxsize)
        self._stop_event = threading.Event()

    def push_frame(self, frame_id: int, frame_data: Any) -> bool:
        """Frame queue me add karta hai. Agar queue full ho to sabse purana frame drop kar deta hai."""
        if self.frame_queue.full():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                pass
        self.frame_queue.put((frame_id, frame_data))
        return True

    def get_frame(self, timeout: float = 0.1) -> Optional[Tuple[int, Any]]:
        """AI Worker thread dwara frame receive karne ke liye."""
        try:
            return self.frame_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def push_result(self, frame_id: int, result: Any):
        """Processed detection results output display ke liye save karta hai."""
        if self.result_queue.full():
            try:
                self.result_queue.get_nowait()
            except queue.Empty:
                pass
        self.result_queue.put((frame_id, result))

    def get_result(self, timeout: float = 0.01) -> Optional[Tuple[int, Any]]:
        """Rendering loop ke liye latest detection output nikalta hai."""
        try:
            return self.result_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def qsize(self) -> int:
        return self.frame_queue.qsize()

    def clear(self):
        with self.frame_queue.mutex:
            self.frame_queue.queue.clear()
        with self.result_queue.mutex:
            self.result_queue.queue.clear()

if __name__ == "__main__":
    manager = DetectionQueueManager(maxsize=5)
    print("--- Testing Multithreaded Detection Queue ---")
    
    for i in range(1, 7):
        manager.push_frame(i, f"Raw_Frame_{i}")
        print(f"Pushed Frame {i} | Queue Size: {manager.qsize()}")

    retrieved = manager.get_frame()
    print(f"Retrieved Frame for AI processing: {retrieved}")
    print(f"Queue Size after retrieval: {manager.qsize()}")