import cv2
import time
import os
import sys
import threading
import logging
from datetime import datetime
from database.db import save_camera, update_camera_status, get_camera, get_all_cameras

logger = logging.getLogger("SentinelX.CameraManager")

DEFAULT_RTSP_CONFIG = {
    "timeout_ms": 5000,
    "buffer_size": 1,
    "transport": "tcp",
    "max_reconnect_delay": 30.0,
    "reconnect_backoff_factor": 1.5,
}


class CameraStream:
    """Individual Camera Monitor Thread handling auto-reconnect, FPS, latency, recording, and snapshots."""
    def __init__(self, name, ip_url, zone="DEFAULT", reconnect_delay=5, rtsp_config=None):
        self.name = name
        self.ip_url = ip_url
        self.zone = zone
        self.reconnect_delay = reconnect_delay
        self.rtsp_config = {**DEFAULT_RTSP_CONFIG, **(rtsp_config or {})}

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

        # Network-specific metrics
        self.network_errors = 0
        self.decode_errors = 0
        self.last_error = None

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

    def _is_rtsp(self):
        url = str(self.ip_url)
        return url.startswith("rtsp://") or url.startswith("rtsps://")

    def _pre_configure_rtsp_env(self):
        """Sets RTSP environment variables BEFORE cv2.VideoCapture is called.
        Must be called before connection so FFmpeg picks up the transport setting."""
        if not self._is_rtsp():
            return

        transport = self.rtsp_config.get("transport", "tcp")
        if transport == "tcp":
            os.environ["OPENCV_FFMPEG_TRANSPORT"] = "tcp"
        elif transport == "udp":
            os.environ["OPENCV_FFMPEG_TRANSPORT"] = "udp"
        elif transport == "auto":
            os.environ.pop("OPENCV_FFMPEG_TRANSPORT", None)

        logger.info(f"[{self.name}] RTSP env set: transport={transport}")

    def _configure_rtsp(self, cap):
        """Applies RTSP-specific OpenCV properties to reduce latency and improve stability."""
        if not self._is_rtsp():
            return

        try:
            timeout_ms = int(self.rtsp_config.get("timeout_ms", 5000))
            buffer_size = int(self.rtsp_config.get("buffer_size", 1))

            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, timeout_ms)
            cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, timeout_ms)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)

            logger.info(f"[{self.name}] RTSP configured: timeout={timeout_ms}ms, buffer={buffer_size}")
        except Exception as e:
            logger.warning(f"[{self.name}] Failed to configure RTSP properties: {e}")

    def _calculate_backoff(self):
        """Calculates exponential backoff delay based on reconnect count."""
        factor = self.rtsp_config.get("reconnect_backoff_factor", 1.5)
        max_delay = self.rtsp_config.get("max_reconnect_delay", 30.0)
        delay = min(self.reconnect_delay * (factor ** self.reconnects), max_delay)
        return delay

    def _capture_loop(self):
        frame_count = 0
        fps_start_time = time.time()

        while self.is_running:
            try:
                ping_start = time.time()
                if self.cap is None or not self.cap.isOpened():
                    self.status = "CONNECTING"
                    self.health = "POOR"
                    self._sync_db()

                    # Set RTSP transport env BEFORE connecting
                    self._pre_configure_rtsp_env()

                    target = int(self.ip_url) if str(self.ip_url).isdigit() else self.ip_url
                    # Use FFMPEG backend for RTSP (CAP_DSHOW doesn't support network streams)
                    if self._is_rtsp():
                        backend = cv2.CAP_FFMPEG
                    elif sys.platform.startswith("win"):
                        backend = cv2.CAP_DSHOW
                    else:
                        backend = 0
                    self.cap = cv2.VideoCapture(target, backend)

                    if self._is_rtsp():
                        self._configure_rtsp(self.cap)

                    if not self.cap.isOpened():
                        self.status = "OFFLINE"
                        self.health = "CRITICAL"
                        self.network_errors += 1
                        self.reconnects += 1
                        self._sync_db()
                        backoff = self._calculate_backoff()
                        logger.warning(f"[{self.name}] Connection failed. Retrying in {backoff:.1f}s...")
                        time.sleep(backoff)
                        continue
                    else:
                        self.status = "ONLINE"
                        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        self.resolution = f"{w}x{h}" if w > 0 else "1920x1080"
                        logger.info(f"[{self.name}] Connected successfully ({self.resolution})")

                ret, frame = self.cap.read()
                self.latency = round((time.time() - ping_start) * 1000, 2)  # ms

                if not ret:
                    self.last_error = "Frame read failed"
                    logger.warning(f"[{self.name}] Frame drop / network interruption.")
                    self.status = "DISCONNECTED"
                    self.health = "POOR"
                    self.network_errors += 1
                    self.reconnects += 1
                    if self.cap:
                        self.cap.release()
                        self.cap = None
                    self._sync_db()
                    backoff = self._calculate_backoff()
                    time.sleep(backoff)
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
                    if self.fps >= 15 and self.latency < 100 and self.network_errors == 0:
                        self.health = "EXCELLENT"
                    elif self.fps >= 8 and self.network_errors < 5:
                        self.health = "GOOD"
                    else:
                        self.health = "POOR"

                    # Reset error counters periodically
                    if self.network_errors > 0:
                        self.network_errors = max(0, self.network_errors - 1)

                    self._sync_db()

            except Exception as e:
                self.last_error = str(e)
                logger.error(f"[{self.name}] capture loop error: {e}")
                self.status = "ERROR"
                self.health = "CRITICAL"
                self.decode_errors += 1
                self._sync_db()
                time.sleep(self.reconnect_delay)

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
            "zone": self.zone,
            "network_errors": self.network_errors,
            "decode_errors": self.decode_errors,
            "last_error": self.last_error,
            "is_rtsp": self._is_rtsp()
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
                uptime=uptime_sec,
                network_errors=self.network_errors,
                decode_errors=self.decode_errors,
                last_error=self.last_error
            )
        except Exception as e:
            logger.error(f"Error syncing camera {self.name} to DB: {e}")


class CameraPipeline:
    """Per-camera pipeline: CameraStream + Queue + Worker + Event State."""
    def __init__(self, name, ip_url, zone="DEFAULT", rtsp_config=None, reconnect_delay=5, max_queue_size=30):
        self.name = name
        self.zone = zone
        self.max_queue_size = max_queue_size

        # Camera stream
        self.stream = CameraStream(name, ip_url, zone, reconnect_delay=reconnect_delay, rtsp_config=rtsp_config)

        # Per-camera queue
        from ai.queue_manager import DetectionQueueManager
        self.queue = DetectionQueueManager(maxsize=max_queue_size)

        # Per-camera event state
        from events.event_manager import EventManager
        from events.memory_manager import MemoryManager
        from events.zone_manager import ZoneManager
        from events.abandoned_object import AbandonedObjectDetector
        from events.crowd_detector import CrowdDetector
        from events.fall_detector import FallDetector
        from events.line_crossing import LineCrossingDetector
        from events.weapon_detector import WeaponDetector
        from events.people_counter import PeopleCounter
        from analytics.heatmap import Heatmap

        self.event_manager = EventManager()
        self.memory_manager = MemoryManager()
        self.zone_manager = ZoneManager()
        self.abandoned_detector = AbandonedObjectDetector()
        self.fall_detector = FallDetector()
        self.crowd_detector = CrowdDetector()
        self.line_detector = LineCrossingDetector()
        self.weapon_detector = WeaponDetector()
        self.people_counter = PeopleCounter()
        self.heatmap = Heatmap()

        # Inference engine and worker (created on start)
        self.worker = None
        self.engine = None
        self.health = None
        self.is_running = False
        self._frame_thread = None
        self._frame_id = 0

    def start(self, model_path=None):
        """Starts the camera pipeline."""
        if self.is_running:
            return

        from ai.health import AIHealthMonitor
        from ai.inference import YOLOInferenceEngine
        from ai.worker import YOLOWorker
        from config import MODEL_PATH

        if model_path is None:
            model_path = MODEL_PATH

        self.health = AIHealthMonitor()
        self.engine = YOLOInferenceEngine(model_path=model_path, health_monitor=self.health)
        self.worker = YOLOWorker(self.queue, self.engine, self.health, on_result=self._on_inference_result)

        self.stream.start()
        self.worker.start()
        self.is_running = True

        # Start frame-forwarding thread (CameraStream → Detection Queue)
        self._frame_thread = threading.Thread(target=self._frame_forward_loop, daemon=True)
        self._frame_thread.start()

    def stop(self):
        """Stops the camera pipeline."""
        self.is_running = False
        if self._frame_thread and self._frame_thread.is_alive():
            self._frame_thread.join(timeout=2.0)
            self._frame_thread = None
        if self.worker:
            self.worker.stop()
            self.worker.join(timeout=2.0)
            self.worker = None
        if self.stream:
            self.stream.stop()
        self.queue.clear()

    def _on_inference_result(self, frame_id, detections, frame_data, annotated_frame=None):
        """Processes inference results: events, alerts, evidence."""
        h = getattr(frame_data, 'shape', None)
        w = h[1] if h is not None and len(h) > 1 else 640
        h = h[0] if h is not None and len(h) > 0 else 360

        person_count = 0
        person_locations = {}
        events = []

        for det in detections:
            cls_id = det["class_id"]
            track_id = det.get("track_id")
            x1, y1, x2, y2 = det["bbox"]
            cx = ((x1 + x2) / 2) / w
            cy = ((y1 + y2) / 2) / h

            if cls_id == 0:
                person_count += 1
                if track_id is None:
                    continue

                self.people_counter.update(track_id, cy)
                self.heatmap.update(cx * w, cy * h)

                line_event = self.line_detector.update(track_id, cy)
                if line_event:
                    events.append(line_event)

                zone = self.zone_manager.get_zone(cx, cy)
                person_locations[track_id] = zone

        crowd_event = self.crowd_detector.detect(person_count)
        if crowd_event:
            events.append(crowd_event)

        detector_events = self.event_manager.process(detections)
        if detector_events:
            events.extend(detector_events)

        abandoned_events = self.abandoned_detector.update(detections)
        if abandoned_events:
            events.extend(abandoned_events)

        fall_events = self.fall_detector.detect(detections)
        if fall_events:
            events.extend(fall_events)

        weapon_events = self.weapon_detector.detect(detections)
        if weapon_events:
            events.extend(weapon_events)

        overall_threat = "LOW"
        for event in events:
            track_id = event.get("track_id")

            if track_id is None:
                zone = "SAFE"
                duration = 0
            else:
                zone = person_locations.get(track_id, "SAFE")
                self.memory_manager.update(track_id, zone)
                duration = self.memory_manager.get_duration(track_id)

                if self.memory_manager.check_loitering(track_id):
                    event["type"] = "LOITERING"

            if event.get("type") == "ABANDONED_OBJECT":
                severity = "HIGH"
                zone = "SAFE"
            else:
                from alerts.intelligence_engine import IntelligenceEngine
                engine = IntelligenceEngine()
                severity = engine.evaluate(event, zone, duration, person_count)

            overall_threat = self._update_threat_level(overall_threat, severity)

            event["zone"] = zone
            event["severity"] = severity
            event["duration"] = int(duration)
            event["camera"] = self.name

            from database.db import save_event
            event_id = save_event(
                event_type=event["type"],
                severity=severity,
                camera=self.name,
                zone=zone,
                confidence=event.get("confidence", 0.0),
                duration=int(duration),
                track_id=track_id if track_id is not None else -1,
                metadata={"duration": int(duration)}
            )

            from dashboard.store import add_event
            add_event({
                "type": event["type"],
                "zone": zone,
                "severity": severity,
                "duration": int(duration)
            })

            from dashboard.timeline import add_incident
            add_incident({
                "time": datetime.now().strftime("%H:%M:%S"),
                "event": event["type"],
                "zone": zone,
                "severity": severity
            })

            from alerts.alert_manager import AlertManager
            alert_mgr = AlertManager()
            alert = alert_mgr.process(event)
            if alert:
                print(f"[{self.name}] [ALERT] {alert['level']} : {alert['message']}")

            if (
                event["type"] in ["LOITERING", "FALL_DETECTED", "ABANDONED_OBJECT", "WEAPON_DETECTED"]
                or event["zone"] == "RESTRICTED"
                or event["severity"] == "HIGH"
            ):
                from evidence.evidence_manager import EvidenceManager
                evidence_mgr = EvidenceManager()
                evidence_frame = annotated_frame if annotated_frame is not None else frame_data
                evidence_mgr.save(
                    evidence_frame,
                    event["type"],
                    track_id if track_id is not None else -1,
                    event_id=event_id,
                    camera=self.name
                )

        if annotated_frame is not None:
            try:
                from dashboard.stream import set_frame
                set_frame(annotated_frame)
            except Exception:
                pass

    def _frame_forward_loop(self):
        """Polls CameraStream for new frames and pushes them into the detection queue."""
        import time as _time
        from config import FRAME_SKIP, INFERENCE_INTERVAL

        frame_skip = max(1, int(FRAME_SKIP))
        interval = max(0.005, float(INFERENCE_INTERVAL))

        while self.is_running:
            try:
                frame = self.stream.get_frame()
                if frame is None:
                    _time.sleep(0.03)
                    continue

                self._frame_id += 1

                if self._frame_id % frame_skip != 0:
                    continue

                self.queue.push_frame(self._frame_id, frame)
                _time.sleep(interval)

            except Exception as e:
                logger.error(f"[{self.name}] Frame forward error: {e}")
                _time.sleep(0.05)

    def _update_threat_level(self, current_threat: str, severity: str) -> str:
        if severity == "HIGH":
            return "HIGH"
        if severity == "MEDIUM" and current_threat != "HIGH":
            return "MEDIUM"
        return current_threat

    def get_frame(self):
        """Gets the latest frame from the camera stream."""
        return self.stream.get_frame()

    def get_queue_size(self):
        """Gets the current frame queue size."""
        return self.queue.qsize()

    def get_status(self):
        """Gets the combined status of the pipeline."""
        stream_details = self.stream.get_details()
        if self.health:
            health_status = self.health.get_health_status()
            stream_details["pipeline_status"] = health_status.get("pipeline_status", "Unknown")
            stream_details["worker_status"] = "Running" if (self.worker and self.worker.is_alive()) else "Stopped"
            stream_details["queue_size"] = self.queue.qsize()
            stream_details["inference_ms"] = health_status.get("metrics", {}).get("last_inference_ms", 0.0)
        return stream_details


class CameraManager:
    """Singleton Manager controlling multi-camera streams and routing Phase 2 APIs."""
    _instance = None
    _default_camera_created = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CameraManager, cls).__new__(cls)
            cls._instance.pipelines = {}
        return cls._instance

    def _ensure_default_camera(self):
        if not self._default_camera_created and "Camera_01" not in self.pipelines:
            pipeline = self.add_camera(name="Camera_01", ip_url=0, zone="Main Entrance", auto_start=True)
            self._default_camera_created = True
            return pipeline
        return self.pipelines.get("Camera_01")

    def add_camera(self, name, ip_url, zone="DEFAULT", rtsp_config=None, reconnect_delay=5, max_queue_size=30, auto_start=True):
        """Adds a new camera with its own independent pipeline."""
        if name in self.pipelines:
            self.remove_camera(name)

        pipeline = CameraPipeline(
            name=name,
            ip_url=ip_url,
            zone=zone,
            rtsp_config=rtsp_config,
            reconnect_delay=reconnect_delay,
            max_queue_size=max_queue_size
        )
        self.pipelines[name] = pipeline

        if auto_start:
            pipeline.start()
        if name == "Camera_01":
            self._default_camera_created = True
        return pipeline

    def remove_camera(self, name):
        """Removes a camera and stops its pipeline."""
        if name in self.pipelines:
            self.pipelines[name].stop()
            del self.pipelines[name]
        if name == "Camera_01":
            self._default_camera_created = False

    def get_camera_stream(self, name="Camera_01"):
        """Gets the camera stream for backward compatibility."""
        pipeline = self.pipelines.get(name)
        if pipeline:
            return pipeline.stream

        if not self.pipelines and name == "Camera_01":
            self._ensure_default_camera()
            pipeline = self.pipelines.get(name)
            if pipeline and getattr(pipeline, "worker", None):
                try:
                    pipeline.worker.stop()
                    pipeline.worker.join(timeout=1.0)
                except Exception:
                    pass
                pipeline.worker = None
            return pipeline.stream if pipeline else None
        return None

    def get_pipeline(self, name):
        """Gets the full pipeline for a camera."""
        return self.pipelines.get(name)

    def get_all_status(self):
        """Gets status of all cameras."""
        self._ensure_default_camera()
        cameras_status = {}
        for name, pipeline in self.pipelines.items():
            cameras_status[name] = pipeline.get_status()
        return cameras_status

    def get_all_streams(self):
        """Gets all camera streams for iteration."""
        self._ensure_default_camera()
        return {name: pipeline.stream for name, pipeline in self.pipelines.items()}

    def stop_all(self):
        """Stops all cameras and pipelines."""
        for name in list(self.pipelines.keys()):
            self.remove_camera(name)
        self._default_camera_created = False

    def release(self):
        """Alias for stop_all for backward compatibility."""
        self.stop_all()


# Global Singleton Instance
camera_manager = CameraManager()
