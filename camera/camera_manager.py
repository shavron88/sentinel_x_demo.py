import cv2
import time
import threading
import logging
from database.db import save_camera, update_camera_status, get_camera, get_all_cameras

logger = logging.getLogger("SentinelX.CameraManager")

class CameraStream:
    """Individual Camera Monitor Thread handling auto-reconnect, FPS, and latency."""
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

        self._thread = None
        self._lock = threading.Lock()

        # Save camera metadata to Database
        save_camera(self.name, self.ip_url, self.zone)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.start_time = time.time()
            self._thread = threading.Thread(target=self._capture_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.status = "OFFLINE"
        self._sync_db()

    def _capture_loop(self):
        frame_count = 0
        fps_start_time = time.time()

        while self.is_running:
            ping_start = time.time()
            if self.cap is None or not self.cap.isOpened():
                self.status = "CONNECTING"
                self.health = "POOR"
                self._sync_db()

                # Attempt connection (supports integer webcam indices or IP RTSP strings)
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
            self.latency = round((time.time() - ping_start) * 1000, 2) # in ms

            if not ret:
                logger.warning(f"Camera [{self.name}] frame drop / disconnected.")
                self.status = "DISCONNECTED"
                self.health = "POOR"
                self.reconnects += 1
                self.cap.release()
                self._sync_db()
                time.sleep(self.reconnect_delay)
                continue

            # Update latest frame
            with self.lock:
                self.latest_frame = frame

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

    def _sync_db(self):
        uptime_sec = int(time.time() - self.start_time) if self.start_time else 0
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


class CameraManager:
    """Manager singleton to control multiple camera streams simultaneously."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CameraManager, cls).__new__(cls)
            cls._instance.cameras = {}
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

    def get_camera_stream(self, name):
        return self.cameras.get(name)

    def get_all_status(self):
        return get_all_cameras()