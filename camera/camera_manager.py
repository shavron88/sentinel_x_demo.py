import cv2
import time
import os
import threading
import logging
from datetime import datetime
from database.db import save_camera, update_camera_status, get_camera, get_all_cameras

logger = logging.getLogger("SentinelX.CameraManager")

class CameraStream:
    """Individual Camera Monitor Thread handling auto-reconnect, FPS, latency, recording, and snapshots."""
    def __init__(self, name, ip_url, zone="DEFAULT", reconnect_delay=5):
        self.name = name
        self.ip_url = ip_url
        self.zone = zone
        self.reconnect_delay = reconnect_delay

        self.cap = None
        self.is_running = False
        self.status = "OFFLINE"
        self.health = "POOR"
        self.fps = 0.0
        self.latency = 0.0
        self.resolution = "UNKNOWN"
        self.reconnects = 0
        self.start_time = None
        self.latest_frame = None

        # Recording & Snapshot State
        self.is_recording = False
        self.video_writer = None
        self.recording_filepath = None

        self._thread = None
        self._lock = threading.Lock()

        # Directories
        self.snapshot_dir = os.path.join("evidence", "screenshots")
        self.video_dir = os.path.join("evidence", "videos")
        os.makedirs(self.snapshot_dir, exist_ok=True)
        os.makedirs(self.video_dir, exist_ok=True)

        # Save camera metadata to Database
        try:
            save_camera(self.name, str(self.ip_url), self.zone)
        except Exception as e:
            logger.error(f"Error saving camera to DB: {e}")

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.start_time = time.time()
            self._thread = threading.Thread(target=self._capture_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self.is_running = False
        if self.is_recording:
            self.stop_recording()
        if self.cap:
            self.cap.release()
        self.status = "OFFLINE"
        self._sync_db()

    def restart(self):
        """Restarts the underlying cv2 capture connection."""
        with self.lock:
            if self.cap:
                self.cap.release()
                self.cap = None
        self.status = "RECONNECTING"

    def _capture_loop(self):
        frame_count = 0
        fps_start_time = time.time()

        while self.is_running:
            ping_start = time.time()
            if self.cap is None or not self.cap.isOpened():
                self.status = "CONNECTING"
                self.health = "POOR"
                self._sync_db()

                target = int(self.ip_url) if str(self.ip_url).isdigit() else self.ip_url
                self.cap = cv2.VideoCapture(target)

                if not self.cap.isOpened():
                    self.status = "OFFLINE"
                    self.health = "CRITICAL"
                    self.reconnects += 1
                    self._sync_db()
                    time.sleep(self.reconnect_delay)
                    continue
                else:
                    self.status = "ONLINE"
                    w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    self.resolution = f"{w}x{h}" if w > 0 else "1920x1080"

            ret, frame = self.cap.read()
            self.latency = round((time.time() - ping_start) * 1000, 2)  # ms

            if not ret:
                logger.warning(f"Camera [{self.name}] frame drop / disconnected.")
                self.status = "DISCONNECTED"
                self.health = "POOR"
                self.reconnects += 1
                if self.cap:
                    self.cap.release()
                    self.cap = None
                self._sync_db()
                time.sleep(self.reconnect_delay)
                continue

            # Update latest frame
            with self.lock:
                self.latest_frame = frame.copy()

            # Handle Video Recording Frame Writing
            if self.is_recording and self.video_writer is not None:
                self.video_writer.write(frame)

            # Calculate FPS
            frame_count += 1
            elapsed = time.time() - fps_start_time
            if elapsed >= 1.0:
                self.fps = round(frame_count / elapsed, 1)
                frame_count = 0
                fps_start_time = time.time()

                # Evaluate Health Status
                if self.fps >= 15 and self.latency < 100:
                    self.health = "EXCELLENT"
                elif self.fps >= 8:
                    self.health = "GOOD"
                else:
                    self.health = "POOR"

                self._sync_db()

    @property
    def lock(self):
        return self._lock

    def get_frame(self):
        with self.lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None

    def take_snapshot(self):
        """Captures current frame and saves image file."""
        frame = self.get_frame()
        if frame is None:
            return False, "No active frame available"

        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filename = f"snapshot_{self.name}_{timestamp}.jpg"
        filepath = os.path.join(self.snapshot_dir, filename)

        success = cv2.imwrite(filepath, frame)
        if success:
            relative_path = f"evidence/screenshots/{filename}"
            return True, relative_path
        return False, "Failed to save snapshot to disk"

    def start_recording(self):
        """Starts writing frame pipeline to MP4 file."""
        if self.is_recording:
            return False, "Recording already active"

        frame = self.get_frame()
        if frame is None:
            return False, "No active frame to start recording"

        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filename = f"rec_{self.name}_{timestamp}.mp4"
        self.recording_filepath = os.path.join(self.video_dir, filename)

        h, w = frame.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(self.recording_filepath, fourcc, 20.0, (w, h))

        self.is_recording = True
        return True, f"evidence/videos/{filename}"

    def stop_recording(self):
        """Stops active recording writer."""
        if not self.is_recording:
            return False, "No active recording"

        self.is_recording = False
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None

        saved_file = self.recording_filepath
        self.recording_filepath = None
        return True, saved_file

    def get_details(self):
        """Returns JSON serializable status representation."""
        return {
            "name": self.name,
            "status": self.status,
            "fps": self.fps,
            "latency": self.latency,
            "health": self.health,
            "resolution": self.resolution,
            "reconnects": self.reconnects,
            "is_recording": self.is_recording,
            "zone": self.zone
        }

    def _sync_db(self):
        uptime_sec = int(time.time() - self.start_time) if self.start_time else 0
        try:
            update_camera_status(
                name=self.name,
                status=self.status,
                fps=self.fps,
                latency=self.latency,
                health=self.health,
                resolution=self.resolution,
                reconnects=self.reconnects,
                uptime=uptime_sec
            )
        except Exception as e:
            logger.error(f"Error syncing camera {self.name} to DB: {e}")


class CameraManager:
    """Singleton Manager controlling multi-camera streams and routing Phase 2 APIs."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CameraManager, cls).__new__(cls)
            cls._instance.cameras = {}
            # Default Camera Init (Webcam 0)
            cls._instance.add_camera(name="Camera_01", ip_url=0, zone="Main Entrance")
        return cls._instance

    def add_camera(self, name, ip_url, zone="DEFAULT"):
        if name in self.cameras:
            self.cameras[name].stop()

        cam = CameraStream(name, ip_url, zone)
        self.cameras[name] = cam
        cam.start()
        return cam

    def remove_camera(self, name):
        if name in self.cameras:
            self.cameras[name].stop()
            del self.cameras[name]

    def get_camera_stream(self, name="Camera_01"):
        return self.cameras.get(name)

    def get_all_status(self):
        cameras_status = {}
        for name, cam in self.cameras.items():
            cameras_status[name] = cam.get_details()
        return cameras_status

# Global Singleton Instance
camera_manager = CameraManager()