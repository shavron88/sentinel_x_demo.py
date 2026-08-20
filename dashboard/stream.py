import cv2
import time
import logging
from datetime import datetime

logger = logging.getLogger("SentinelX.Stream")

_latest_frame = None
_frame_timestamp = 0.0
_frame_drops = 0
_last_fps_time = time.time()
_fps_frame_count = 0
_current_fps = 0.0

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


def set_frame(frame):
    global _latest_frame, _frame_timestamp
    _latest_frame = frame
    _frame_timestamp = time.time()
    _update_fps()


def get_frame():
    global _latest_frame
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


def generate(camera_name="Camera_01", camera_status="ONLINE", queue_size=0):
    """
    Stream generator that prefers AI-annotated frames, falls back to CameraManager.
    """
    global _frame_drops

    from camera.camera_manager import camera_manager

    while True:
        frame = get_frame()

        if frame is None:
            stream = camera_manager.get_camera_stream(camera_name)
            if stream:
                frame = stream.get_frame()
            if frame is None:
                _frame_drops += 1
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
