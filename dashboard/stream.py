import cv2
import threading
import time

output_frame = None
lock = threading.Lock()


def set_frame(frame):
    global output_frame

    print("Frame updated")

    with lock:
        output_frame = frame.copy()
def generate():
    """MJPEG stream generator for Flask."""
    global output_frame

    while True:

        with lock:
            if output_frame is None:
                frame = None
            else:
                ret, buffer = cv2.imencode(".jpg", output_frame)
                frame = buffer.tobytes() if ret else None

        if frame is None:
            time.sleep(0.03)
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )