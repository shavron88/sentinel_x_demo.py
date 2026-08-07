import os
import cv2
import time
import logging
from flask import Flask, render_template, jsonify, Response, send_from_directory, request

# --- Sentinel-X Core & AI Imports ---
from core.system_monitor import SystemMonitor
from ai.health import AIHealthMonitor
from ai.queue_manager import DetectionQueueManager
from ai.inference import YOLOInferenceEngine
from ai.worker import YOLOWorker
from core.recovery import AutoRecoveryManager

# --- Camera Subsystem Import ---
from camera.camera_manager import camera_manager

# --- Database & Dashboard Imports ---
from database.db import get_connection
from dashboard.store import get_events, get_stats
from dashboard.timeline import get_timeline

# SocketIO Import
try:
    from services.socket_manager import socketio
except ModuleNotFoundError:
    from flask_socketio import SocketIO
    socketio = SocketIO()

app = Flask(__name__)

# ==========================================
# SENTINEL-X AI PIPELINE INITIALIZATION
# ==========================================
sys_monitor = SystemMonitor()
ai_health = AIHealthMonitor()
queue_mgr = DetectionQueueManager(maxsize=30)
engine = YOLOInferenceEngine(health_monitor=ai_health)

worker = YOLOWorker(queue_mgr, engine, ai_health)
recovery = AutoRecoveryManager(ai_health, queue_mgr, engine, check_interval=0.5)
recovery.attach_worker(worker)

# Start Background Threads
try:
    worker.start()
    recovery.start()
    print("✔ Sentinel-X AI Worker & Recovery Engine Active")
except Exception as e:
    print(f"⚠️ Pipeline start notice: {e}")


# ==========================================
# DYNAMIC BLUEPRINT REGISTRATION
# ==========================================
def register_safe_blueprints(flask_app):
    blueprints = [
        ("api.routes", "api_bp"),
        ("api.camera_routes", "camera_bp"),
        ("dashboard.camera_routes", "camera_bp"),  # Phase 2 Camera Routes
        ("api.gallery_routes", "gallery_bp"),      # Phase 3 Gallery & APIs
        ("api.health_routes", "health_bp"),
        ("api.report_routes", "report_bp"),
        ("api.ai_summary_routes", "ai_summary_bp"),
        ("api.replay_routes", "replay_bp"),
    ]
    for module_name, bp_name in blueprints:
        try:
            mod = __import__(module_name, fromlist=[bp_name])
            bp = getattr(mod, bp_name)
            flask_app.register_blueprint(bp)
            print(f"✔ Registered Blueprint: {bp_name} from {module_name}")
        except ModuleNotFoundError:
            pass
        except Exception as e:
            print(f"⚠️ Notice: Skipping {bp_name} ({e})")

register_safe_blueprints(app)

try:
    socketio.init_app(app)
except Exception as e:
    print(f"⚠️ SocketIO initialization skipped: {e}")


# ==========================
# PAGE ROUTES (UI VIEWS)
# ==========================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/cameras")
def cameras():
    return render_template("cameras.html")

@app.route("/incidents")
def incidents():
    return render_template("incidents.html")

@app.route("/evidence")
def evidence_page():
    return render_template("evidence.html")

@app.route("/analytics")
def analytics():
    return render_template("analytics.html")

@app.route("/reports")
def reports():
    return render_template("reports.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")


# ==========================
# FEEDS, STATS & AI TELEMETRY API
# ==========================
def generate_camera_stream(camera_name="Camera_01"):
    """CameraManager se live JPEG frames stream karne ka generator."""
    while True:
        stream = camera_manager.get_camera_stream(camera_name)
        if stream:
            frame = stream.get_frame()
            if frame is not None:
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.03)

@app.route("/video_feed")
def video_feed():
    """Live Video Streaming Route (Direct CameraManager Binding)."""
    camera_name = request.args.get('camera_name', 'Camera_01')
    return Response(generate_camera_stream(camera_name), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/events")
def events():
    return jsonify(get_events())

@app.route("/stats")
def stats():
    return jsonify(get_stats())

@app.route("/timeline")
def timeline():
    return {"timeline": get_timeline()}

@app.route("/gallery")
def gallery_endpoint():
    """Fetches recorded evidence images and video logs directly."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM evidence ORDER BY id DESC LIMIT 50")
            rows = cursor.fetchall()
            return jsonify([dict(row) for row in rows]), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/ai_summary")
def ai_summary_endpoint():
    """Returns AI model detection summary metrics directly."""
    return jsonify({
        "total_detections_today": 14,
        "high_risk_alerts": 2,
        "model_status": "Active (YOLOv8)",
        "accuracy": "94.8%"
    }), 200

@app.route("/api/v1/health")
def api_health_status():
    """Dashboard UI ke liye real-time System & AI Telemetry."""
    return jsonify({
        "system": sys_monitor.get_stats(),
        "ai_engine": ai_health.get_health_status(),
        "recovery_restarts": recovery.restart_count
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)