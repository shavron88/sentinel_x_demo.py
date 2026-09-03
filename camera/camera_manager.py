import cv2
import time
import os
import sys
import threading
import logging
from datetime import datetime
from typing import List
from database.db import save_camera, update_camera_status, get_camera, get_all_cameras

from camera.video_evidence import EvidenceVideoWatcher
from camera.video_perspective import VideoPerspectiveValidator
from camera.video_preprocessor import VideoPreprocessor

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
        self._last_error_time = 0.0
        self._last_db_sync = 0.0

        # Recording & Snapshot State
        self.is_recording = False
        self.video_writer = None
        self.recording_filepath = None

        self._thread = None
        self._lock = threading.Lock()

        # Detect if source is a video file (for EOF handling)
        self._is_video = self._is_video_file()
        # Per-frame delay for real-time video file playback (set on connect)
        self._video_frame_delay = 0.0

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
        self._safe_release()
        self.status = "OFFLINE"
        self._sync_db()

    def restart(self):
        """Restarts the underlying cv2 capture connection."""
        with self.lock:
            if self.cap:
                try:
                    self.cap.release()
                except Exception as e:
                    logger.warning(f"[{self.name}] cv2 capture release error during restart (ignored): {e}")
                self.cap = None
        self.status = "RECONNECTING"
        self._sync_db()

    def _is_rtsp(self):
        url = str(self.ip_url)
        return url.startswith("rtsp://") or url.startswith("rtsps://")

    def _is_video_file(self):
        """Check if the source is a video file (not a live stream or webcam index)."""
        url = str(self.ip_url)
        # Webcam indices are digits (0, 1, 2)
        if url.isdigit():
            return False
        # RTSP/HTTP streams are not local files
        if url.startswith(("rtsp://", "rtsps://", "http://", "https://")):
            return False
        # Check if it's a file path that exists or has a video extension
        video_extensions = ('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v')
        if any(url.lower().endswith(ext) for ext in video_extensions):
            return True
        # Check if it's an existing file
        if os.path.isfile(url):
            return True
        return False

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

    def _open_capture(self, target, preferred_backend):
        """Open a cv2.VideoCapture robustly, falling back to the default backend.

        Some OpenCV/Windows DShow configurations raise an unrecoverable C++
        exception for device indices, so every backend attempt is guarded and
        we always fall back to the platform default backend.
        Returns an open VideoCapture or None.
        """
        backends_to_try = [preferred_backend]
        if preferred_backend != 0:
            backends_to_try.append(0)
        for be in backends_to_try:
            try:
                cap = cv2.VideoCapture(target, be)
            except Exception as e:
                logger.warning(f"[{self.name}] cv2.VideoCapture(backend={be}) failed: {e}")
                continue
            if cap is not None and cap.isOpened():
                return cap
            try:
                cap.release()
            except Exception:
                pass
        # Last resort: no explicit backend
        try:
            cap = cv2.VideoCapture(target)
            if cap is not None and cap.isOpened():
                return cap
            try:
                cap.release()
            except Exception:
                pass
        except Exception as e:
            logger.warning(f"[{self.name}] default cv2.VideoCapture failed: {e}")
        return None

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
                    # Use FFMPEG backend for RTSP streams and video files
                    # (CAP_DSHOW only supports capture devices). For local capture
                    # devices use the platform default backend — it is more robust
                    # than DShow on Windows OpenCV builds, where DShow can raise an
                    # unrecoverable C++ exception for some device indices.
                    if self._is_rtsp() or self._is_video:
                        backend = cv2.CAP_FFMPEG
                    else:
                        backend = 0
                    self.cap = self._open_capture(target, backend)

                    if self.cap is not None and self._is_rtsp():
                        self._configure_rtsp(self.cap)

                    if self.cap is None or not self.cap.isOpened():
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
                        self.health = "HEALTHY"
                        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        self.resolution = f"{w}x{h}" if w > 0 else "1920x1080"
                        logger.info(f"[{self.name}] Connected successfully ({self.resolution})")
                        self._sync_db()
                        # Native frame rate pacing for video files (real-time playback)
                        if self._is_video:
                            vfps = self.cap.get(cv2.CAP_PROP_FPS)
                            self._video_frame_delay = (1.0 / vfps) if (vfps and vfps > 0) else 0.0

                ret, frame = self.cap.read()
                read_time = time.time() - ping_start
                self.latency = round(read_time * 1000, 2)  # ms

                if read_time > 5.0:
                    logger.warning(f"[{self.name}] Frame read timeout ({read_time:.1f}s), releasing capture")
                    self.last_error = f"Read timeout ({read_time:.1f}s)"
                    self._last_error_time = time.time()
                    self.status = "RECONNECTING"
                    self._safe_release()
                    self._sync_db()
                    time.sleep(1.0)
                    continue

                if not ret:
                    # Video file reached EOF — loop back to frame 0 so it behaves
                    # like a continuous surveillance feed for the hackathon demo.
                    # The same CameraStream / DetectionQueueManager / YOLO / tracking
                    # pipeline keeps running; only the capture position resets.
                    if self._is_video:
                        logger.info(f"[{self.name}] Video file reached EOF; looping to frame 0.")
                        if self.cap and self.cap.isOpened():
                            seek_ok = self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            if seek_ok:
                                self.status = "ONLINE"
                                self.network_errors = 0
                                self.reconnects = 0
                                self._sync_db()
                                continue
                        # If seek failed, release and let the top of the loop reopen
                        self.status = "RECONNECTING"
                        self._safe_release()
                        self._sync_db()
                        continue

                    # Live stream disconnect — reconnect with backoff
                    self.last_error = "Frame read failed"
                    self._last_error_time = time.time()
                    logger.warning(f"[{self.name}] Frame drop / network interruption.")
                    self.status = "DISCONNECTED"
                    self.health = "POOR"
                    self.network_errors += 1
                    self.reconnects += 1
                    self._safe_release()
                    self._sync_db()
                    backoff = self._calculate_backoff()
                    time.sleep(backoff)
                    continue

                # Update latest frame
                with self.lock:
                    self.latest_frame = frame.copy()

                # Pace video files to their native frame rate (mimics a live CCTV
                # feed and avoids max-speed decoding overloading the CPU)
                if self._is_video and self._video_frame_delay > 0:
                    spent = time.time() - ping_start
                    if spent < self._video_frame_delay:
                        time.sleep(self._video_frame_delay - spent)

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
                self._last_error_time = time.time()
                logger.error(f"[{self.name}] capture loop error: {e}")
                self.status = "ERROR"
                self.health = "CRITICAL"
                self.decode_errors += 1
                self._safe_release()
                self._sync_db()
                time.sleep(self.reconnect_delay)

    @property
    def lock(self):
        return self._lock

    def get_frame(self):
        with self.lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None

    def _safe_release(self):
        """Releases the cv2 capture handle defensively (DShow can raise on release)."""
        if self.cap:
            try:
                self.cap.release()
            except Exception as e:
                logger.warning(f"[{self.name}] cv2 capture release error (ignored): {e}")
        self.cap = None

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
            "is_rtsp": self._is_rtsp(),
            "is_video_file": self._is_video
        }

    def _sync_db(self):
        now = time.time()
        if now - self._last_db_sync < 2.0:
            return
        self._last_db_sync = now
        
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
    def __init__(
        self,
        name,
        ip_url,
        zone="DEFAULT",
        rtsp_config=None,
        reconnect_delay=5,
        max_queue_size=30,
        validator=None,
        preprocessor=None,
    ):
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

        # Live detection summary (per-camera AI display for the dashboard)
        self.last_person_count = 0
        self.last_vehicle_count = 0
        self.last_detections = []  # [{label, confidence}]
        self.last_detection_time = 0.0

        # Perspective validation and preprocessing
        self.validator = validator
        self.preprocessor = preprocessor

    def start(self, model_path=None, skip_worker=False, shared_engine=None):
        """Starts the camera pipeline."""
        if self.is_running:
            return

        from ai.health import AIHealthMonitor
        from ai.inference import YOLOInferenceEngine
        from config import MODEL_PATH

        if model_path is None:
            model_path = MODEL_PATH

        self.health = AIHealthMonitor()
        if shared_engine is not None:
            self.engine = shared_engine
        else:
            self.engine = YOLOInferenceEngine(model_path=model_path, health_monitor=self.health, camera_id=self.name)

        if not skip_worker:
            from ai.worker import YOLOWorker
            self.worker = YOLOWorker(self.queue, self.engine, self.health, on_result=self._on_inference_result)
            self.worker.start()

        self.stream.start()
        self.is_running = True

        if not skip_worker:
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
        vehicle_count = 0
        person_locations = {}
        events = []
        detection_summary = []

        for det in detections:
            cls_id = det["class_id"]
            track_id = det.get("track_id")
            x1, y1, x2, y2 = det["bbox"]
            cx = ((x1 + x2) / 2) / w
            cy = ((y1 + y2) / 2) / h

            label = str(det.get("label", "")).lower()
            detection_summary.append({"label": label, "confidence": det.get("confidence", 0.0)})
            if cls_id == 0 or label == "person":
                person_count += 1
            elif label in ("car", "bus", "truck", "motorcycle", "bicycle", "van"):
                vehicle_count += 1

            if cls_id == 0:
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

        # Update live per-camera detection summary (real YOLO results only)
        self.last_person_count = person_count
        self.last_vehicle_count = vehicle_count
        self.last_detections = detection_summary[:8]  # capped for UI display
        self.last_detection_time = time.time()

        if annotated_frame is not None:
            try:
                from dashboard.stream import set_frame
                set_frame(annotated_frame, camera_name=self.name)
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

                if self.preprocessor is not None:
                    frame = self.preprocessor.process(frame)

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
        stream_details["persons"] = self.last_person_count
        stream_details["vehicles"] = self.last_vehicle_count
        stream_details["detections"] = self.last_detections
        stream_details["last_detection_time"] = self.last_detection_time
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
    _current_user_id = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CameraManager, cls).__new__(cls)
            cls._instance.pipelines = {}
            cls._instance._video_watcher = EvidenceVideoWatcher(
                watch_dir="evidence/videos",
                poll_interval=5.0
            )
            cls._instance._video_watcher.register_callback(cls._instance._on_new_video_evidence)
            cls._instance._validator = VideoPerspectiveValidator()
            cls._instance._preprocessor = VideoPreprocessor()
            cls._instance._shared_engine = None
            cls._instance._shared_engine_health = None
            cls._instance._default_camera_created = True
        return cls._instance

    def _get_shared_engine(self):
        if self._shared_engine is None:
            from ai.health import AIHealthMonitor
            from ai.inference import YOLOInferenceEngine
            from config import MODEL_PATH
            self._shared_engine_health = AIHealthMonitor()
            self._shared_engine = YOLOInferenceEngine(
                model_path=MODEL_PATH,
                health_monitor=self._shared_engine_health,
                camera_id="shared"
            )
        return self._shared_engine

    def _ensure_default_camera(self):
        if not self._default_camera_created and "Camera_01" not in self.pipelines:
            pipeline = self.add_camera(
                name="Camera_01",
                ip_url=1,
                zone="Main Entrance",
                auto_start=True,
                validator=self._validator,
                preprocessor=self._preprocessor,
            )
            self._default_camera_created = True
            return pipeline
        return self.pipelines.get("Camera_01")

    def _on_new_video_evidence(self, filepath: str):
        """Callback from EvidenceVideoWatcher when a new video file appears."""
        try:
            filename = os.path.basename(filepath)
            base_name = os.path.splitext(filename)[0]
            camera_name = f"Evidence_{base_name}"

            if camera_name in self.pipelines:
                logger.info(f"[VideoEvidence] Camera '{camera_name}' already registered.")
                return

            shared_engine = self._get_shared_engine()
            logger.info(f"[VideoEvidence] Registering new evidence camera: {camera_name} -> {filepath}")
            pipeline = self.add_camera(
                name=camera_name,
                ip_url=filepath,
                zone="Evidence",
                auto_start=True,
                validator=self._validator,
                preprocessor=self._preprocessor,
                skip_worker=True,
                shared_engine=shared_engine,
            )
            try:
                save_camera(
                    name=camera_name,
                    stream_url=filepath,
                    location="Evidence",
                    status="ONLINE",
                    user_id=self._current_user_id or 1,
                    is_rtsp=0
                )
            except Exception as db_err:
                logger.error(f"[VideoEvidence] Failed to save camera to DB: {db_err}")
        except Exception as e:
            logger.error(f"[VideoEvidence] Callback error: {e}")

    def start_video_watcher(self):
        if hasattr(self, '_video_watcher') and self._video_watcher:
            self._video_watcher.start()

    def stop_video_watcher(self):
        if hasattr(self, '_video_watcher') and self._video_watcher:
            self._video_watcher.stop()

    def get_video_evidence_cameras(self) -> List[str]:
        if not hasattr(self, '_video_watcher') or not self._video_watcher:
            return []
        files = self._video_watcher.get_known_files()
        names = []
        for filepath in files:
            filename = os.path.basename(filepath)
            base_name = os.path.splitext(filename)[0]
            names.append(f"Evidence_{base_name}")
        return names

    def load_cameras_for_user(self, user_id):
        """Stop all cameras and load only the specified user's cameras from DB."""
        self.stop_all()
        self._current_user_id = user_id
        self._default_camera_created = False

        try:
            from database.db import get_all_cameras
            cameras = get_all_cameras(user_id=user_id)
            for cam in cameras:
                self.add_camera(
                    name=cam.get("name", ""),
                    ip_url=cam.get("stream_url", ""),
                    zone=cam.get("location", "General Area"),
                    auto_start=True,
                    validator=self._validator,
                    preprocessor=self._preprocessor,
                )
        except Exception as e:
            print(f"Error loading cameras for user {user_id}: {e}")

    def add_camera(self, name, ip_url, zone="DEFAULT", rtsp_config=None, reconnect_delay=5, max_queue_size=30, auto_start=True, validator=None, preprocessor=None, skip_worker=False, shared_engine=None):
        """Adds a new camera with its own independent pipeline."""
        if name in self.pipelines:
            self.remove_camera(name)

        pipeline = CameraPipeline(
            name=name,
            ip_url=ip_url,
            zone=zone,
            rtsp_config=rtsp_config,
            reconnect_delay=reconnect_delay,
            max_queue_size=max_queue_size,
            validator=validator,
            preprocessor=preprocessor,
        )
        self.pipelines[name] = pipeline

        if auto_start:
            pipeline.start(skip_worker=skip_worker, shared_engine=shared_engine)
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
        self.stop_video_watcher()

    def release(self):
        """Alias for stop_all for backward compatibility."""
        self.stop_all()


# Global Singleton Instance
camera_manager = CameraManager()
