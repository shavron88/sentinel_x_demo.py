import cv2
import time

def generate():
    """
    Captures live frames from local webcam (Index 0)
    and yields them as JPEG byte stream for Flask.
    """
    # Open default camera (Try 0, or 1 if using an external webcam)
    cap = cv2.VideoCapture(0)

    # Check if camera opened successfully
    if not cap.isOpened():
        print("❌ Error: Could not open camera/webcam.")
        return

    while True:
        success, frame = cap.read()
        if not success:
            time.sleep(0.1)
            continue

        # Overlay text on feed
        cv2.putText(
            frame, 
            "SENTINEL-X LIVE MONITOR", 
            (20, 35), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.7, 
            (0, 255, 0), 
            2
        )

        # Compress/Encode frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        frame_bytes = buffer.tobytes()

        # Yield frame in multipart format for browser HTTP stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        # Limit frame rate to save CPU (~30 FPS)
        time.sleep(0.03)

    cap.release()