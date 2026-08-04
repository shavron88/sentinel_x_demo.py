import os
import logging
from flask import Flask, render_template, jsonify, Response, send_from_directory

from dashboard.store import get_events, get_stats
from dashboard.timeline import get_timeline

# Stream Import
try:
    from dashboard.stream import generate
except ImportError:
    def generate():
        yield b""

# SocketIO Import
try:
    from services.socket_manager import socketio
except ModuleNotFoundError:
    from flask_socketio import SocketIO
    socketio = SocketIO()

app = Flask(__name__)

# --- Blueprint Registration ---
def register_safe_blueprints(flask_app):
    blueprints = [
        ("api.routes", "api_bp"),
        ("api.camera_routes", "camera_bp"),
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
            print(f"✔ Registered Blueprint: {bp_name}")
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
# FEEDS & STATS
# ==========================
@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/events")
def events():
    return jsonify(get_events())

@app.route("/stats")
def stats():
    return jsonify(get_stats())

@app.route("/timeline")
def timeline():
    return {"timeline": get_timeline()}