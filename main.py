import time
import sys
import os

from core.system_monitor import SystemMonitor
from ai.health import AIHealthMonitor
from ai.queue_manager import DetectionQueueManager
from ai.inference import YOLOInferenceEngine
from ai.worker import YOLOWorker
from core.recovery import AutoRecoveryManager


class SentinelXPipeline:
    def __init__(self):
        print("[SENTINEL-X] Initializing Core Architecture...")
        self.sys_monitor = SystemMonitor()
        self.ai_health = AIHealthMonitor()
        self.queue_mgr = DetectionQueueManager(maxsize=30)
        self.engine = YOLOInferenceEngine(health_monitor=self.ai_health)
        
        self.worker = YOLOWorker(self.queue_mgr, self.engine, self.ai_health)
        self.recovery = AutoRecoveryManager(self.ai_health, self.queue_mgr, self.engine, check_interval=0.5)
        self.recovery.attach_worker(self.worker)

    def start(self):
        print("[SENTINEL-X] Starting Pipeline Threads...")
        self.worker.start()
        self.recovery.start()
        print("[SENTINEL-X] Pipeline Active & Self-Healing Enabled.\n")

    def run_demo(self, duration_sec: int = 5):
        start_time = time.time()
        frame_id = 0

        try:
            while time.time() - start_time < duration_sec:
                frame_id += 1
                # 1. Frame queue me push karein
                self.queue_mgr.push_frame(frame_id, f"Frame_Data_{frame_id}")

                # 2. Output result fetch karein
                res = self.queue_mgr.get_result()

                # 3. Telemetry status display karein
                sys_stats = self.sys_monitor.get_stats()
                ai_stats = self.ai_health.get_health_status()

                print(
                    f"[Frame {frame_id}] "
                    f"CPU: {sys_stats['cpu_usage_percent']}% | "
                    f"RAM: {sys_stats['ram_usage_percent']}% | "
                    f"AI Status: {ai_stats['status']} | "
                    f"FPS: {ai_stats['metrics']['detection_fps']} | "
                    f"Queue Size: {ai_stats['metrics']['queue_size']}"
                )

                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n[SENTINEL-X] Stopping pipeline manually...")

        self.stop()

    def stop(self):
        print("\n[SENTINEL-X] Shutting down pipeline components...")
        self.recovery.stop()
        if self.recovery.worker:
            self.recovery.worker.stop()
            self.recovery.worker.join(timeout=1.0)
        print("[SENTINEL-X] All components shut down cleanly.")


if __name__ == "__main__":
    pipeline = SentinelXPipeline()
    pipeline.start()
    pipeline.run_demo(duration_sec=3)