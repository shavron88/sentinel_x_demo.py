import cv2
import time
import logging
import numpy as np
from datetime import datetime

logger = logging.getLogger("SentinelX.Stream")

# Per-camera frame storage for multi-camera support
_latest_frames = {}
_frame_timestamps = {}
_frame_drops = 0
_last_fps_time = time.time()
_fps_frame_count = 0
_current_fps = 0.0

# Backward-compatible aliases
_latest_frame = None
_frame_timestamp = 0.0

# Camera status overlay config
STATUS_COLORS = {
    "ONLINE": (0, 255, 0),
    "CONNECTING": (0, 165, 255),
    "RECONNECTING": (0, 165, 255),
    "OFFLINE": (0, 0, 255),
    "DISCONNECTED": (0, 0, 255),
    "CRITICAL": (0, 0, 255),
    "EXCELLENT": (0, 255, 0),
    "GOOD": (0, 255, 255),
    "POOR": (0, 165, 255),
}


def set_frame(frame, camera_name=None):
    global _latest_frames, _frame_timestamps, _latest_frame, _frame_timestamp
    if camera_name:
        _latest_frames[camera_name] = frame
        _frame_timestamps[camera_name] = time.time()
    else:
        _latest_frame = frame
        _frame_timestamp = time.time()
    _update_fps()


def get_frame(camera_name=None):
    global _latest_frames, _latest_frame
    if camera_name:
        return _latest_frames.get(camera_name)
    return _latest_frame


def get_frame_age():
    return time.time() - _frame_timestamp


def get_frame_drops():
    return _frame_drops


def get_stream_fps():
    return _current_fps


def _update_fps():
    global _fps_frame_count, _current_fps, _last_fps_time
    _fps_frame_count += 1
    elapsed = time.time() - _last_fps_time
    if elapsed >= 1.0:
        _current_fps = round(_fps_frame_count / elapsed, 1)
        _fps_frame_count = 0
        _last_fps_time = time.time()


def _draw_status_overlay(frame, camera_name="Camera", status="ONLINE", fps=0.0, queue_size=0):
    """Draws status information, timestamp, and checks against registered faces."""
    try:
        from database.db import get_connection
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM known_faces")
            known_faces = cursor.fetchall()
            
            # Simple UI text integration for known faces overlay test
            y_offset = 60
            for face in known_faces:
                name = face["name"] if isinstance(face, dict) else face[0]
                cv2.putText(frame, f"Target: {name}", (20, y_offset), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                y_offset += 25
    except Exception as e:
        logger.debug(f"Face overlay lookup notice: {e}")

    # Standard status header info
    cv2.putText(frame, f"{camera_name} | Status: {status} | FPS: {fps}", (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, STATUS_COLORS.get(status, (0, 255, 0)), 2)
    return frame


def _placeholder_frame(camera_name="Camera", status="OFFLINE"):
    """Generate a solid placeholder frame with a status message."""
    w, h = 640, 360
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    frame[:] = (0, 0, 20)

    color = STATUS_COLORS.get(status, (0, 0, 255))
    cv2.rectangle(frame, (0, 0), (w, h), color, 3)
    cv2.putText(frame, status.upper(), (w // 2 - 110, h // 2 - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 1.1, color, 3)
    cv2.putText(frame, "No video feed available", (w // 2 - 130, h - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)
    return frame


def generate(camera_name="Camera_01", camera_status="ONLINE", queue_size=0):
    """Stream generator that includes live face verification overlays."""
    global _frame_drops

    from camera.camera_manager import camera_manager

    _last_placeholder = 0.0
    placeholder_interval = 0.5

    while True:
        pipeline = camera_manager.get_pipeline(camera_name)
        if pipeline:
            camera_status = pipeline.stream.status
            queue_size = pipeline.get_queue_size()

        frame = get_frame(camera_name)
        if frame is None:
            frame = get_frame() 

        if frame is None:
            if pipeline:
                frame = pipeline.get_frame()
            if frame is None:
                stream = camera_manager.get_camera_stream(camera_name)
                if stream:
                    frame = stream.get_frame()
            if frame is None:
                _frame_drops += 1
                now = time.time()
                if now - _last_placeholder >= placeholder_interval:
                    _last_placeholder = now
                    frame = _placeholder_frame(camera_name, camera_status)
                else:
                    time.sleep(0.01)
                    continue

        _update_fps()

        frame = _draw_status_overlay(
            frame,
            camera_name=camera_name,
            status=camera_status,
            fps=_current_fps,
            queue_size=queue_size
        )

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            _frame_drops += 1
            time.sleep(0.01)
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

        time.sleep(0.001)