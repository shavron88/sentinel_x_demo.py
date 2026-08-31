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
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 90), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)

    color = STATUS_COLORS.get(status, (255, 255, 255))

    cv2.putText(frame, f"{camera_name}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Status: {status}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    cv2.putText(frame, f"FPS: {fps:.1f}", (200, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(frame, f"Queue: {queue_size}", (300, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    if status in ["OFFLINE", "DISCONNECTED", "CRITICAL"]:
        cv2.putText(frame, "SIGNAL LOST", (w // 2 - 80, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

    return frame


def _placeholder_frame(camera_name="Camera", status="OFFLINE"):
    """Generate a solid placeholder frame with a status message.

    Keeps the MJPEG stream alive (so the browser does not hang / go black) when
    no real frame is available from the camera or AI pipeline.
    """
    w, h = 640, 360
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    frame[:] = (0, 0, 20)

    color = STATUS_COLORS.get(status, (0, 0, 255))
    cv2.rectangle(frame, (0, 0), (w, h), color, 3)
    cv2.putText(frame, status.upper(), (w // 2 - 110, h // 2 - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 1.1, color, 3)
    cv2.putText(frame, camera_name, (w // 2 - 90, h // 2 + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    cv2.putText(frame, "No video feed available", (w // 2 - 130, h - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)
    return frame


def generate(camera_name="Camera_01", camera_status="ONLINE", queue_size=0):
    """
    Stream generator that prefers AI-annotated frames (per-camera), falls back to CameraManager.
    Refreshes live camera status from the pipeline each frame (ONLINE / ENDED / OFFLINE ...).
    Yields a placeholder frame when no real frame is available so the browser feed
    never hangs or goes black.
    """
    global _frame_drops

    from camera.camera_manager import camera_manager

    _last_placeholder = 0.0

    while True:
        # Live status from the pipeline (kept current: EOF -> ENDED, drops -> OFFLINE)
        pipeline = camera_manager.get_pipeline(camera_name)
        if pipeline:
            camera_status = pipeline.stream.status
            queue_size = pipeline.get_queue_size()

        # Prefer per-camera AI-annotated frame, then global, then raw stream
        frame = get_frame(camera_name)

        if frame is None:
            frame = get_frame()  # fallback to global

        if frame is None:
            stream = camera_manager.get_camera_stream(camera_name)
            if stream:
                frame = stream.get_frame()
            if frame is None:
                _frame_drops += 1
                # Yield a placeholder periodically so the MJPEG client does not
                # stall; real frames take precedence when they become available.
                now = time.time()
                if now - _last_placeholder >= 0.5:
                    _last_placeholder = now
                    frame = _placeholder_frame(camera_name, camera_status)
                else:
                    time.sleep(0.03)
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
            time.sleep(0.03)
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

        time.sleep(0.001)
