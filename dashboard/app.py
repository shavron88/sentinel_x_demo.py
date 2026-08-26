import os
import cv2
import time
import json
import logging
import secrets
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from flask import Flask, render_template, jsonify, Response, send_from_directory, send_file, request, session, redirect, url_for

# --- Sentinel-X Core & AI Imports ---
from core.system_monitor import SystemMonitor
from ai.health import AIHealthMonitor
from ai.queue_manager import DetectionQueueManager
from ai.inference import YOLOInferenceEngine
from ai.worker import YOLOWorker
from core.recovery import AutoRecoveryManager

# --- Authentication ---
from api.auth import (
    is_authenticated, login, logout,
    get_csrf_token, validate_csrf_token,
    require_auth, require_csrf, rate_limit
)

# --- Camera Subsystem Import ---
from camera.camera_manager import camera_manager

# --- Database & Dashboard Imports ---
from database.db import get_connection
from dashboard.store import get_events, get_stats
from dashboard.timeline import get_timeline
from dashboard.settings_store import SettingsStore

# SocketIO Import
try:
    from services.socket_manager import socketio
except ModuleNotFoundError:
    from flask_socketio import SocketIO
    socketio = SocketIO()

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))

<<<<<<< HEAD
# --- Production Security Headers & Cookies ---
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=True  # Production mein HTTPS ke sath True karein
)

=======
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
# ==========================================
# SENTINEL-X AI PIPELINE INITIALIZATION
# ==========================================
from config import MODEL_PATH as _MODEL_PATH

sys_monitor = SystemMonitor()
ai_health = AIHealthMonitor()
queue_mgr = DetectionQueueManager(maxsize=30)
engine = YOLOInferenceEngine(model_path=_MODEL_PATH, health_monitor=ai_health)

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
        ("dashboard.camera_routes", "camera_bp"),
        ("api.gallery_routes", "gallery_bp"),
        ("api.health", "health_bp"),
        ("api.report_routes", "replay_bp"),
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
# ERROR HANDLERS
# ==========================
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/sentinelx_errors.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.ERROR)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.ERROR)

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Server Error: {error}", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled Exception: {e}", exc_info=True)
    if request.is_json:
        return jsonify({"error": "An unexpected error occurred"}), 500
    return jsonify({"error": "An unexpected error occurred"}), 500


# ==========================
# AUTHENTICATION ENDPOINTS
# ==========================

@app.route("/api/auth/login", methods=["POST"])
@rate_limit
def api_login():
    """Authenticate user and create session."""
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")
    
    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"status": "error", "message": "Invalid request format"}), 400
    
    if len(username) > 100 or len(password) > 100:
        return jsonify({"status": "error", "message": "Request too large"}), 400
    
    success, message = login(username, password)
    
    if success:
        return jsonify({
            "status": "success",
            "message": message,
            "username": session.get("username"),
            "csrf_token": get_csrf_token()
        }), 200
    
    return jsonify({"status": "error", "message": message}), 401


@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    """Log out the current user."""
    logout()
    return jsonify({"status": "success", "message": "Logged out successfully"}), 200


@app.route("/api/auth/status", methods=["GET"])
def api_auth_status():
    """Check current authentication status."""
    if is_authenticated():
        return jsonify({
            "authenticated": True,
            "username": session.get("username"),
            "email": session.get("email"),
            "role": session.get("role"),
            "csrf_token": get_csrf_token()
        }), 200
    
    return jsonify({"authenticated": False}), 200


@app.route("/api/auth/csrf-token", methods=["GET"])
def api_csrf_token():
    """Get CSRF token for state-changing requests."""
    if not is_authenticated():
        return jsonify({"error": "Authentication required"}), 401
    
    return jsonify({"csrf_token": get_csrf_token()}), 200


# ==========================
# ROUTE PROTECTION
# ==========================

<<<<<<< HEAD
=======
# Endpoints that do NOT require authentication
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
_PUBLIC_ENDPOINTS = frozenset({
    "login_page", "static", "api_login", "api_auth_status",
    "api_logout", "api_csrf_token",
    "not_found_error", "internal_error", "handle_exception",
    "health_bp.get_system_health",
})

_PUBLIC_PREFIXES = ("static",)


@app.before_request
def _enforce_auth():
    """Redirect unauthenticated users to the login page.
    API endpoints receive a 401 JSON response instead of a redirect."""
    ep = request.endpoint
    if ep is None:
<<<<<<< HEAD
        return  

=======
        return  # Let Flask handle 404

    # Allow public endpoints
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
    if ep in _PUBLIC_ENDPOINTS:
        return
    for prefix in _PUBLIC_PREFIXES:
        if ep.startswith(prefix + "."):
            return

    if not is_authenticated():
<<<<<<< HEAD
=======
        # API / data endpoints get 401 JSON
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
        if request.path.startswith("/api/") or \
           request.path.startswith("/video_feed") or \
           request.path.startswith("/download_") or \
           request.path.startswith("/evidence/screenshots") or \
           request.path in ("/events", "/stats", "/timeline",
                            "/gallery", "/ai_summary",
                            "/analytics_data", "/reports_data"):
            return jsonify({"error": "Authentication required",
                            "status": "unauthorized"}), 401
<<<<<<< HEAD
=======
        # Page routes redirect to login
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
        return redirect(url_for("login_page"))


# ==========================
# LOGIN PAGE
# ==========================

@app.route("/login")
def login_page():
<<<<<<< HEAD
    """Render the authentication landing page."""
=======
    """Render the authentication landing page.
    Already-authenticated users are sent to the dashboard."""
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
    if is_authenticated():
        return redirect(url_for("home"))
    return render_template("login.html")


# ==========================
# PAGE ROUTES (UI VIEWS)
# ==========================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/cameras")
def cameras():
    return render_template("cameras.html")

@app.route("/camera_view")
def camera_view():
    camera_name = request.args.get('camera', 'Camera_01')
    return render_template("camera_view.html", camera_name=camera_name)

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

@app.route("/live_wall")
def live_wall():
    return render_template("live_wall.html")

@app.route("/security_map")
def security_map():
    return render_template("security_map.html")

@app.route("/threat_center")
def threat_center():
    return render_template("threat_center.html")

@app.route("/command_center")
def command_center():
    return render_template("command_center.html")

@app.route("/copilot")
def copilot():
    return render_template("copilot.html")

@app.route("/replay")
def replay():
    return render_template("replay.html")

@app.route("/notifications")
def notifications_page():
    return render_template("notifications.html")


@app.route("/api/copilot", methods=["POST"])
def api_copilot():
<<<<<<< HEAD
=======
    """Copilot chat endpoint - returns pending status if not implemented."""
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
    return jsonify({
        "response": "Backend integration pending. AI chat functionality is not yet connected to a language model.",
        "status": "pending"
    }), 200

@app.route("/settings")
def settings():
    return render_template("settings.html")


# ==========================
# LIVE STREAM GENERATORS
# ==========================
from dashboard.stream import generate as stream_generate

def generate_camera_stream(camera_name="Camera_01"):
<<<<<<< HEAD
=======
    """Stream generator that uses AI-annotated frames when available."""
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
    from camera.camera_manager import camera_manager
    
    camera_status = "ONLINE"
    queue_size = 0

    pipeline = camera_manager.get_pipeline(camera_name)
    if pipeline and pipeline.is_running:
        camera_status = pipeline.stream.status
        queue_size = pipeline.get_queue_size()

    for frame in stream_generate(
        camera_name=camera_name,
        camera_status=camera_status,
        queue_size=queue_size
    ):
        if pipeline:
            camera_status = pipeline.stream.status
            queue_size = pipeline.get_queue_size()
        yield frame

@app.route("/video_feed")
def video_feed():
<<<<<<< HEAD
=======
    """Live Video Streaming Route (Direct CameraManager Binding)."""
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
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

@app.route("/api/storage")
def api_storage():
<<<<<<< HEAD
=======
    """Returns actual storage usage for evidence files."""
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
    total_size = 0
    screenshots_dir = os.path.join("evidence", "screenshots")
    if os.path.isdir(screenshots_dir):
        for dirpath, dirnames, filenames in os.walk(screenshots_dir):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total_size += os.path.getsize(fp)
                except OSError:
                    pass
    return jsonify({
        "storage_bytes": total_size,
        "storage_gb": round(total_size / (1024 ** 3), 2)
    })


@app.route("/gallery")
def gallery_endpoint():
<<<<<<< HEAD
=======
    """Fetches recorded evidence images and video logs directly."""
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
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
<<<<<<< HEAD
=======
    """Returns AI model detection summary metrics directly."""
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
    try:
        from dashboard.store import get_stats
        stats = get_stats()
        risk = "LOW"
        if stats.get("high_severity_incidents", 0) > 5:
            risk = "HIGH"
        elif stats.get("high_severity_incidents", 0) > 0:
            risk = "MEDIUM"
        return jsonify({
            "risk": risk,
            "detections": stats.get("total_incidents", 0),
            "confidence": f"{stats.get('online_cameras', 0) * 20 + 75:.1f}%",
            "recommendation": "Review high-risk alerts" if risk != "LOW" else "Continue Monitoring"
        }), 200
    except Exception as e:
        return jsonify({
            "risk": "LOW",
            "detections": 0,
            "confidence": "0%",
            "recommendation": "Continue Monitoring"
        }), 200

@app.route("/api/v1/health")
def api_health_status():
<<<<<<< HEAD
=======
    """Dashboard UI ke liye real-time System & AI Telemetry."""
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
    return jsonify({
        "system": sys_monitor.get_stats(),
        "ai_engine": ai_health.get_health_status(),
        "recovery_restarts": recovery.restart_count
    })


@app.route("/api/demo/scenarios", methods=["GET"])
def api_demo_scenarios():
<<<<<<< HEAD
=======
    """Returns available demo scenarios."""
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
    from events.demo_controller import demo_controller
    return jsonify({
        "scenarios": list(demo_controller.scenarios.keys())
    }), 200


@app.route("/api/demo/trigger", methods=["POST"])
def api_demo_trigger():
<<<<<<< HEAD
=======
    """Triggers a synthetic demo scenario."""
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
    from events.demo_controller import demo_controller
    data = request.get_json() or {}
    scenario = data.get("scenario", "")
    camera = data.get("camera", "Demo Camera")
    zone = data.get("zone", "General Area")
    
    if not scenario:
        return jsonify({"success": False, "error": "Scenario name is required."}), 400
    
    result = demo_controller.trigger(scenario, camera=camera, zone=zone)
    if result.get("success"):
        return jsonify(result), 200
    return jsonify(result), 400


@app.route("/analytics_data")
def analytics_data():
<<<<<<< HEAD
=======
    """Returns aggregated analytics data for the analytics page."""
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
    try:
        from dashboard.store import get_stats, get_events
        from database.db import get_all_evidence
        from collections import Counter
        
        stats = get_stats()
        events = get_events(limit=200)
        evidence = get_all_evidence(limit=200)
        
        total_incidents = stats.get("total_incidents", len(events))
        people = stats.get("persons", 0)
        vehicles = stats.get("vehicles", 0)
        threat = stats.get("threat", "LOW")
        
        event_types = Counter()
        falls = 0
        weapons = 0
        for e in events:
            etype = (e.get("event_type") or "Unknown").lower()
            event_types[etype] += 1
            if "fall" in etype:
                falls += 1
            if "weapon" in etype:
                weapons += 1
        
        labels = list(event_types.keys())
        values = list(event_types.values())
        
        table_events = []
        for e in events[:20]:
            table_events.append({
                "event": e.get("event_type", "Unknown"),
                "time": e.get("timestamp", ""),
                "severity": e.get("severity", "LOW")
            })
        
        return jsonify({
            "total": total_incidents,
            "people": people,
            "vehicles": vehicles,
            "threat": threat,
            "labels": labels,
            "values": values,
            "falls": falls,
            "weapons": weapons,
            "events": table_events
        }), 200
    except Exception as e:
        return jsonify({
<<<<<<< HEAD
            "total": 0, "people": 0, "vehicles": 0, "threat": "UNKNOWN",
            "labels": [], "values": [], "falls": 0, "weapons": 0, "events": []
=======
            "total": 0,
            "people": 0,
            "vehicles": 0,
            "threat": "UNKNOWN",
            "labels": [],
            "values": [],
            "falls": 0,
            "weapons": 0,
            "events": []
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
        }), 200


@app.route("/reports_data")
def reports_data():
<<<<<<< HEAD
=======
    """Returns structured report data for the reports page."""
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
    try:
        from services.report_service import ReportService
        data = ReportService.generate_summary_data(timeframe="daily")
        
        from database.db import get_all_cameras
        cameras = get_all_cameras()
        
<<<<<<< HEAD
        event_summary = [{"name": name, "count": count} for name, count in data.get("breakdown_by_type", {}).items()]
        camera_summary = [{"name": cam.get("name", "Unknown"), "status": cam.get("status", "OFFLINE"), "events": cam.get("event_count", 0)} for cam in cameras]
=======
        event_summary = []
        for name, count in data.get("breakdown_by_type", {}).items():
            event_summary.append({"name": name, "count": count})
        
        camera_summary = []
        for cam in cameras:
            camera_summary.append({
                "name": cam.get("name", "Unknown"),
                "status": cam.get("status", "OFFLINE"),
                "events": cam.get("event_count", 0)
            })
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
        
        evidence_count = 0
        evidence_today = 0
        try:
            from database.db import get_all_evidence
            ev = get_all_evidence(limit=500)
            evidence_count = len(ev)
            today_str = datetime.now().strftime("%Y-%m-%d")
            evidence_today = sum(1 for e in ev if today_str in (e.get("time") or ""))
        except Exception:
            pass
        
        storage_bytes = 0
        try:
            screenshots_dir = os.path.join("evidence", "screenshots")
            if os.path.isdir(screenshots_dir):
                for dirpath, dirnames, filenames in os.walk(screenshots_dir):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        try:
                            storage_bytes += os.path.getsize(fp)
                        except OSError:
                            pass
        except Exception:
            pass
        storage_mb = round(storage_bytes / (1024 * 1024), 2)
        
        high_priority = []
        for e in data.get("recent_samples", [])[:10]:
            if e.get("severity") in ("HIGH", "CRITICAL"):
                high_priority.append({
                    "event": e.get("event_type", "Unknown"),
                    "camera": e.get("camera", "Unknown"),
                    "location": e.get("zone", "Unknown"),
                    "time": e.get("timestamp", "")
                })
        
        return jsonify({
            "camera_online": len([c for c in cameras if c.get("status") == "ONLINE"]),
            "total_events": data["metrics"]["total_incidents"],
            "total_evidence": evidence_count,
            "threat_level": "CRITICAL" if data["metrics"].get("high_severity", 0) > 5 else ("MEDIUM" if data["metrics"].get("high_severity", 0) > 0 else "LOW"),
            "event_summary": event_summary,
            "camera_summary": camera_summary,
<<<<<<< HEAD
            "evidence": {"images": evidence_count, "today": evidence_today, "storage": f"{storage_mb} MB"},
=======
            "evidence": {
                "images": evidence_count,
                "today": evidence_today,
                "storage": f"{storage_mb} MB"
            },
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
            "high_priority": high_priority
        }), 200
    except Exception as e:
        return jsonify({
<<<<<<< HEAD
            "camera_online": 0, "total_events": 0, "total_evidence": 0, "threat_level": "LOW",
            "event_summary": [], "camera_summary": [], "evidence": {"images": 0, "today": 0, "storage": "0 MB"}, "high_priority": []
=======
            "camera_online": 0,
            "total_events": 0,
            "total_evidence": 0,
            "threat_level": "LOW",
            "event_summary": [],
            "camera_summary": [],
            "evidence": {"images": 0, "today": 0, "storage": "0 MB"},
            "high_priority": []
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
        }), 200


@app.route("/download_csv")
def download_csv():
<<<<<<< HEAD
=======
    """Generates and downloads a CSV report."""
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
    try:
        from services.report_service import ReportService
        csv_data = ReportService.generate_csv_report(timeframe="daily")
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=sentinelx_report.csv"}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/download_pdf")
def download_pdf():
<<<<<<< HEAD
=======
    """PDF export is handled client-side via printable HTML report.
    This endpoint provides a redirect hint for direct URL access."""
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
    return jsonify({
        "success": False,
        "error": "PDF export is generated from the Reports page. Use the Export PDF button.",
        "hint": "Navigate to /reports and click the Export PDF button."
    }), 200


@app.route("/api/settings", methods=["GET", "POST"])
@require_auth
<<<<<<< HEAD
@require_csrf  # <-- CSRF Protection Added Here
=======
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
@rate_limit
def api_settings():
    if request.method == "GET":
        settings = SettingsStore.get_all_settings()
        return jsonify(settings)
    else:
        data = request.get_json(silent=True) or {}
        key = data.get("key")
        value = data.get("value")
        if key is None:
            return jsonify({"success": False, "error": "Missing 'key'"}), 400
        success = SettingsStore.set_setting(key, value)
        return jsonify({"success": success}), 200 if success else 500

@app.route("/api/settings/camera", methods=["POST"])
@require_auth
@require_csrf
def api_settings_camera():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"success": False, "error": "Invalid JSON"}), 400
    
    if "cameras" not in data:
        return jsonify({"success": False, "error": "Missing 'cameras' field"}), 400
    
    cameras = data.get("cameras", [])
    if not isinstance(cameras, list):
        return jsonify({"success": False, "error": "Invalid cameras data"}), 400
    results = SettingsStore.save_camera_settings(cameras)
    return jsonify({"success": True, "results": results})

@app.route("/api/settings/notifications", methods=["POST"])
@require_auth
@require_csrf
def api_settings_notifications():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"success": False, "error": "Invalid JSON"}), 400
    
    if "notifications" not in data:
        return jsonify({"success": False, "error": "Missing 'notifications' field"}), 400
    
    notifications = data.get("notifications", {})
    if not isinstance(notifications, dict):
        return jsonify({"success": False, "error": "Invalid notification data"}), 400
    success = SettingsStore.set_setting("notifications", notifications)
    return jsonify({"success": success}), 200 if success else 500

@app.route("/api/system/restart", methods=["POST"])
@require_auth
@require_csrf
def api_system_restart():
    try:
        recovery._restart_worker()
        return jsonify({"success": True, "message": "AI Engine restarted"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/system/backup", methods=["POST"])
@require_auth
@require_csrf
def api_system_backup():
    try:
        import shutil
        backup_path = os.path.join("backups", f"sentinelx_backup_{int(time.time())}.db")
        os.makedirs("backups", exist_ok=True)
        shutil.copy2("sentinelx.db", backup_path)
        return jsonify({"success": True, "path": backup_path}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/system/cleanup", methods=["POST"])
@require_auth
@require_csrf
def api_system_cleanup():
    try:
        cutoff_days = 7
        cutoff = (datetime.now() - timedelta(days=cutoff_days)).strftime("%Y-%m-%d %H:%M:%S")
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM evidence WHERE timestamp < ?", (cutoff,))
            deleted = cursor.rowcount
            conn.commit()
        return jsonify({"success": True, "deleted": deleted}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/evidence/screenshots/<path:filename>")
def evidence_screenshot(filename):
<<<<<<< HEAD
=======
    """Serves stored evidence screenshots using project-root-relative path."""
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
    project_root = os.path.dirname(app.root_path)
    evidence_dir = os.path.join(project_root, "evidence", "screenshots")
    
    safe_filename = secure_filename(filename)
    if not safe_filename:
        return jsonify({"error": "Invalid filename"}), 400
    
    filepath = os.path.join(evidence_dir, safe_filename)
    real_filepath = os.path.realpath(filepath)
    real_evidence_dir = os.path.realpath(evidence_dir)
    
    if not real_filepath.startswith(real_evidence_dir + os.sep) and real_filepath != real_evidence_dir:
        return jsonify({"error": "Access denied"}), 403
    
    if os.path.exists(real_filepath):
        return send_file(real_filepath)
    return jsonify({"error": "Resource not found"}), 404


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")
    app.run(host="127.0.0.1", port=5000, debug=debug_mode)