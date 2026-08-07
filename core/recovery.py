import sys
import os
import time
import threading

# Ensure root import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.health import AIHealthMonitor
from ai.worker import YOLOWorker
from ai.queue_manager import DetectionQueueManager
from ai.inference import YOLOInferenceEngine


class AutoRecoveryManager(threading.Thread):
    def __init__(self, health_monitor: AIHealthMonitor, queue_mgr: DetectionQueueManager, engine: YOLOInferenceEngine, check_interval: float = 1.0):
        super().__init__(daemon=True)
        self.health_monitor = health_monitor
        self.queue_mgr = queue_mgr
        self.engine = engine
        self.check_interval = check_interval
        
        self.worker: YOLOWorker = None
        self.is_running = False
        self.restart_count = 0

    def attach_worker(self, worker: YOLOWorker):
        self.worker = worker

    def _restart_worker(self):
        self.restart_count += 1
        print(f"[RECOVERY MANAGER] Triggering Auto-Recovery (Attempt #{self.restart_count})...")
        self.health_monitor.set_recovery(True)

        if self.worker and self.worker.is_alive():
            self.worker.stop()
            self.worker.join(timeout=1.0)

        # Clear frozen queue
        self.queue_mgr.clear()

        # Re-initialize worker
        self.worker = YOLOWorker(self.queue_mgr, self.engine, self.health_monitor)
        self.worker.start()

        time.sleep(0.5)
        self.health_monitor.set_recovery(False)
        print(f"[RECOVERY MANAGER] AI Worker recovered successfully!")

    def run(self):
        self.is_running = True
        while self.is_running:
            time.sleep(self.check_interval)
            
            health_data = self.health_monitor.get_health_status()
            
            # Check 1: AI Worker died unexpectedly
            worker_dead = self.worker is None or not self.worker.is_alive()
            
            # Check 2: Queue overflowed (> 90% capacity)
            queue_overflow = health_data["metrics"]["queue_capacity_percent"] > 90.0

            if worker_dead or queue_overflow:
                self._restart_worker()

    def stop(self):
        self.is_running = False


if __name__ == "__main__":
    health = AIHealthMonitor()
    queue_mgr = DetectionQueueManager(maxsize=10)
    engine = YOLOInferenceEngine(health_monitor=health)
    
    worker = YOLOWorker(queue_mgr, engine, health)
    recovery = AutoRecoveryManager(health, queue_mgr, engine, check_interval=0.5)
    recovery.attach_worker(worker)

    print("--- Testing Self-Healing & Auto-Recovery Engine ---")
    worker.start()
    recovery.start()

    time.sleep(0.5)
    print("Simulating Worker Crash...")
    worker.stop()  # Forcefully kill worker thread

    time.sleep(1.5)  # Wait for Recovery Manager to detect & restart worker
    
    print(f"Total Recovery Restarts Executed: {recovery.restart_count}")
    print(f"Worker Alive Status: {recovery.worker.is_alive()}")

    recovery.stop()
    if recovery.worker:
        recovery.worker.stop()