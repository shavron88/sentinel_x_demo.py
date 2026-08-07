import cv2
import time

def generate():
    """
    Captures live frames from local laptop webcam (Index 0 or 1)
    using DirectShow backend for Windows.
    """
    # Windows par laptop camera ke liye DirectShow (CAP_DSHOW) best kaam karta hai
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # Agar Index 0 na chale toh Index 1 try karein
    if not cap.isOpened():
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("❌ Error: Laptop camera detect nahi hua.")
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

        time.sleep(0.03)

    cap.release()