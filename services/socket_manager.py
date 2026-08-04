import cv2
import time
import logging
from flask_socketio import SocketIO, emit

logger = logging.getLogger("SentinelX.SocketIO")

# Global SocketIO Instance
socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")


class SocketManager:
    """Centralized Real-Time Event Broadcaster for Dashboard UI."""

    @staticmethod
    def emit_dashboard_stats(stats_data):
        socketio.emit("dashboard_stats", stats_data)

    @staticmethod
    def emit_new_event(event_data):
        socketio.emit("new_event", event_data)

    @staticmethod
    def emit_notification(notification_data):
        socketio.emit("notification", notification_data)

    @staticmethod
    def emit_camera_status(camera_status_data):
        socketio.emit("camera_status", camera_status_data)


@socketio.on("connect")
def handle_connect():
    logger.info("Dashboard Client Connected via SocketIO")
    emit("connection_ack", {"status": "Connected to SentinelX Engine"})


@socketio.on("disconnect")
def handle_disconnect():
    logger.info("Dashboard Client Disconnected")


# --- LIVE VIDEO STREAM GENERATOR ---
def generate_camera_frames():
    """Captures frames from webcam (Index 0) and yields JPEG stream."""
    camera = cv2.VideoCapture(0)  # Change 0 to 1 if using external camera
    
    if not camera.isOpened():
        print("❌ Error: Camera could not be opened.")
        return

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # (Optional) Overlay Live Status Text on Feed
            cv2.putText(
                frame, 
                "SENTINEL-X LIVE FEED", 
                (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, 
                (0, 255, 0), 
                2
            )

            # Encode frame to JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(0.03)  # Approx ~30 FPS balance
    
    camera.release()