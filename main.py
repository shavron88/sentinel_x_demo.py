import time
import sys
import os
import argparse
import json

from core.system_monitor import SystemMonitor
from ai.health import AIHealthMonitor
from ai.queue_manager import DetectionQueueManager
from ai.inference import YOLOInferenceEngine
from ai.worker import YOLOWorker
from core.recovery import AutoRecoveryManager

from camera.camera_manager import CameraManager
from config import DEMO_MODE, CAMERAS, MODEL_PATH, MAX_QUEUE_SIZE


class SentinelXPipeline:
    def __init__(self, demo=False):
        print("[SENTINEL-X] Initializing Core Architecture...")
        self.demo = demo or DEMO_MODE
        self.sys_monitor = SystemMonitor()
        self.ai_health = AIHealthMonitor()
        self.queue_mgr = DetectionQueueManager(maxsize=MAX_QUEUE_SIZE)
        self.engine = YOLOInferenceEngine(model_path=MODEL_PATH, health_monitor=self.ai_health)
        
        self.worker = YOLOWorker(self.queue_mgr, self.engine, self.ai_health)
        self.recovery = AutoRecoveryManager(self.ai_health, self.queue_mgr, self.engine, check_interval=0.5)
        self.recovery.attach_worker(self.worker)
        
        self.camera_manager = None

    def start(self):
        print("[SENTINEL-X] Starting Pipeline Threads...")
        self.worker.start()
        self.recovery.start()
        
        if self.demo:
            print("[SENTINEL-X] Demo Mode: Using synthetic data")
        else:
            self._setup_cameras()
        
        print("[SENTINEL-X] Pipeline Active & Self-Healing Enabled.\n")

    def _setup_cameras(self):
        """Setup cameras from config or environment."""
        self.camera_manager = CameraManager()
        
        if CAMERAS:
            print(f"[SENTINEL-X] Loading {len(CAMERAS)} cameras from configuration...")
            for cam_config in CAMERAS:
                name = cam_config["name"]
                source = cam_config["source"]
                zone = cam_config["zone"]
                timeout = cam_config.get("timeout", 5000)
                
                # Parse source
                if source.isdigit():
                    ip_url = int(source)
                else:
                    ip_url = source
                
                rtsp_config = None
                if str(ip_url).startswith("rtsp://") or str(ip_url).startswith("rtsps://"):
                    rtsp_config = {
                        "timeout_ms": timeout,
                        "buffer_size": 1,
                        "transport": "tcp"
                    }
                
                self.camera_manager.add_camera(
                    name=name,
                    ip_url=ip_url,
                    zone=zone,
                    rtsp_config=rtsp_config
                )
                print(f"[SENTINEL-X]   + {name} ({zone})")
        else:
            print("[SENTINEL-X] Using default camera configuration")

    def run_demo(self, duration_sec: int = 5):
        start_time = time.time()
        frame_id = 0

        try:
            while time.time() - start_time < duration_sec:
                frame_id += 1
                self.queue_mgr.push_frame(frame_id, f"Frame_Data_{frame_id}")
                res = self.queue_mgr.get_result()

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

    def run_multi_camera_demo(self, duration_sec: int = 10):
        """Run multi-camera demonstration."""
        if not self.camera_manager:
            self._setup_cameras()
        
        print(f"[SENTINEL-X] Running multi-camera demo for {duration_sec} seconds...")
        
        start_time = time.time()
        frame_id = 0
        
        try:
            while time.time() - start_time < duration_sec:
                frame_id += 1
                
                # Process each camera
                for name, pipeline in self.camera_manager.pipelines.items():
                    frame = pipeline.get_frame()
                    if frame is not None:
                        # Push to camera-specific queue
                        pipeline.queue.push_frame(frame_id, frame)
                        
                        # Log status
                        status = pipeline.get_status()
                        print(
                            f"[{name}] Frame {frame_id} | "
                            f"Status: {status.get('status')} | "
                            f"FPS: {status.get('fps')} | "
                            f"Queue: {status.get('queue_size')}"
                        )
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n[SENTINEL-X] Stopping multi-camera demo...")
        
        self.stop()

    def stop(self):
        print("\n[SENTINEL-X] Shutting down pipeline components...")
        
        if self.camera_manager:
            self.camera_manager.stop_all()
        
        self.recovery.stop()
        if self.recovery.worker:
            self.recovery.worker.stop()
            self.recovery.worker.join(timeout=1.0)
        print("[SENTINEL-X] All components shut down cleanly.")


def main():
    parser = argparse.ArgumentParser(description="SentinelX AI Surveillance Platform")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode with synthetic data")
    parser.add_argument("--multi-camera", action="store_true", help="Run multi-camera demo")
    parser.add_argument("--duration", type=int, default=10, help="Demo duration in seconds")
    parser.add_argument("--flask", action="store_true", help="Start Flask dashboard server")
    args = parser.parse_args()

    if args.flask:
        print("[SENTINEL-X] Starting Flask Dashboard...")
        from dashboard.app import app
        app.run(host="0.0.0.0", port=5000, debug=True)
        return

    pipeline = SentinelXPipeline(demo=args.demo)
    pipeline.start()

    if args.multi_camera:
        pipeline.run_multi_camera_demo(duration_sec=args.duration)
    else:
        pipeline.run_demo(duration_sec=args.duration)


if __name__ == "__main__":
    main()
