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
    is_authenticated, login, logout, signup,
    get_csrf_token, validate_csrf_token,
    require_auth, require_csrf, rate_limit,
    get_current_user_id
)


def _get_user_id():
    """Get the current user ID from session, defaulting to 1 for backward compatibility."""
    return get_current_user_id()

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

# --- Production Security Headers & Cookies ---
_is_production = os.getenv("FLASK_ENV", "development") == "production"
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=_is_production  # Only require HTTPS in production
)
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
    if request.path.startswith('/api/') or request.is_json or request.headers.get('Accept') == 'application/json':
        return jsonify({"error": "Resource not found"}), 404
    return render_template('base.html', error_page=True, error_code=404, error_message='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Server Error: {error}", exc_info=True)
    if request.path.startswith('/api/') or request.is_json or request.headers.get('Accept') == 'application/json':
        return jsonify({"error": "Internal server error"}), 500
    return render_template('base.html', error_page=True, error_code=500, error_message='Internal server error'), 500

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled Exception: {e}", exc_info=True)
    if request.path.startswith('/api/') or request.is_json or request.headers.get('Accept') == 'application/json':
        return jsonify({"error": "An unexpected error occurred"}), 500
    return render_template('base.html', error_page=True, error_code=500, error_message='An unexpected error occurred'), 500


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
        user_id = get_current_user_id()
        camera_manager.load_cameras_for_user(user_id)
        return jsonify({
            "status": "success",
            "message": message,
            "username": session.get("username"),
            "csrf_token": get_csrf_token()
        }), 200
    
    return jsonify({"status": "error", "message": message}), 401


@app.route("/api/auth/signup", methods=["POST"])
@rate_limit
def api_signup():
    """Register a new user account."""
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")
    email = data.get("email", "")

    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"status": "error", "message": "Invalid request format"}), 400
    if len(username) > 100 or len(password) > 100:
        return jsonify({"status": "error", "message": "Request too large"}), 400

    success, result = signup(username, password, email)
    if success:
        user_id = result
        session.clear()
        session["authenticated"] = True
        session["username"] = username
        session["user_id"] = user_id
        session["email"] = email or f"{username}@sentinelx.ai"
        session["role"] = "System Administrator"
        session["last_active"] = datetime.now().isoformat()
        session["csrf_token"] = secrets.token_hex(32)
        camera_manager.load_cameras_for_user(user_id)
        return jsonify({
            "status": "success",
            "message": "Account created successfully",
            "username": username,
            "csrf_token": get_csrf_token()
        }), 201
    return jsonify({"status": "error", "message": result}), 400


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

# Endpoints that do NOT require authentication
_PUBLIC_ENDPOINTS = frozenset({
    "landing_page", "login_page", "signup_page", "static",
    "api_login", "api_signup", "api_auth_status",
    "api_logout", "api_csrf_token",
    "not_found_error", "internal_error", "handle_exception",
    "health_bp.get_system_health", "api_health_status",
})

_PUBLIC_PREFIXES = ("static",)


@app.before_request
def _enforce_auth():
    """Redirect unauthenticated users to the login page.
    API endpoints receive a 401 JSON response instead of a redirect."""
    ep = request.endpoint
    if ep is None:
        return  # Let Flask handle 404

    # Allow public endpoints
    if ep in _PUBLIC_ENDPOINTS:
        return
    for prefix in _PUBLIC_PREFIXES:
        if ep.startswith(prefix + "."):
            return

    if not is_authenticated():
        # API / data endpoints get 401 JSON
        if request.path.startswith("/api/") or \
           request.path.startswith("/video_feed") or \
           request.path.startswith("/download_") or \
           request.path.startswith("/evidence/screenshots") or \
           request.path in ("/events", "/stats", "/timeline",
                            "/gallery", "/ai_summary",
                            "/analytics_data", "/reports_data"):
            return jsonify({"error": "Authentication required",
                            "status": "unauthorized"}), 401
        # Page routes redirect to login
        return redirect(url_for("login_page"))


# ==========================
# LOGIN PAGE
# ==========================

@app.route("/login")
def login_page():
    """Render the authentication landing page.
    Already-authenticated users are sent to the dashboard."""
    if is_authenticated():
        return redirect(url_for("dashboard_page"))
    return render_template("login.html")


@app.route("/signup")
def signup_page():
    """Render the sign-up page.
    Already-authenticated users are sent to the dashboard."""
    if is_authenticated():
        return redirect(url_for("dashboard_page"))
    return render_template("signup.html")


# ==========================
# PAGE ROUTES (UI VIEWS)
# ==========================
@app.route("/")
def landing_page():
    """Public landing page — no authentication required."""
    return render_template("landing.html")


@app.route("/dashboard")
def dashboard_page():
    """Protected dashboard — requires authentication."""
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
    """Copilot chat endpoint - returns pending status if not implemented."""
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
    """Stream generator that uses AI-annotated frames when available."""
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
    """Live Video Streaming Route (Direct CameraManager Binding)."""
    camera_name = request.args.get('camera_name', 'Camera_01')
    return Response(generate_camera_stream(camera_name), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/events")
def events():
    return jsonify(get_events(user_id=_get_user_id()))

@app.route("/stats")
def stats():
    return jsonify(get_stats(user_id=_get_user_id()))

@app.route("/timeline")
def timeline():
    return {"timeline": get_timeline(user_id=_get_user_id())}

@app.route("/api/storage")
def api_storage():
    """Returns actual storage usage for evidence files."""
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
    """Fetches recorded evidence images and video logs directly."""
    try:
        user_id = _get_user_id()
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM evidence WHERE user_id = ? ORDER BY id DESC LIMIT 50", (user_id,))
            rows = cursor.fetchall()
            return jsonify([dict(row) for row in rows]), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/ai_summary")
def ai_summary_endpoint():
    """Returns AI model detection summary metrics directly."""
    try:
        from dashboard.store import get_stats
        stats = get_stats(user_id=_get_user_id())
        risk = "LOW"
        if stats.get("high_severity_incidents", 0) > 5:
            risk = "HIGH"
        elif stats.get("high_severity_incidents", 0) > 0:
            risk = "MEDIUM"
        return jsonify({
            "risk": risk,
            "detections": stats.get("total_incidents", 0),
            "confidence": f"{min(stats.get('accuracy', stats.get('avg_confidence', 92.5)), 100):.1f}%",
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
    """Dashboard UI ke liye real-time System & AI Telemetry."""
    return jsonify({
        "system": sys_monitor.get_stats(),
        "ai_engine": ai_health.get_health_status(),
        "recovery_restarts": recovery.restart_count
    })


@app.route("/api/demo/scenarios", methods=["GET"])
def api_demo_scenarios():
    """Returns available demo scenarios."""
    from events.demo_controller import demo_controller
    return jsonify({
        "scenarios": list(demo_controller.scenarios.keys())
    }), 200


@app.route("/api/demo/trigger", methods=["POST"])
def api_demo_trigger():
    """Triggers a synthetic demo scenario."""
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
    """Returns aggregated analytics data for the analytics page with date range and filter support."""
    try:
        from dashboard.store import get_stats, get_events
        from database.db import get_all_evidence
        from collections import Counter
        from datetime import datetime, timedelta
        
        user_id = _get_user_id()
        
        # Get query parameters
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        event_types_filter = request.args.get("event_types")
        severity_filter = request.args.get("severity")
        cameras_filter = request.args.get("cameras")
        
        stats = get_stats(user_id=user_id)
        events = get_events(limit=500, user_id=user_id)
        evidence = get_all_evidence(limit=500, user_id=user_id)
        
        # Apply date range filter
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            events = [e for e in events if e.get("timestamp") and datetime.strptime(e.get("timestamp").split(" ")[0], "%Y-%m-%d") >= start_dt]
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            events = [e for e in events if e.get("timestamp") and datetime.strptime(e.get("timestamp").split(" ")[0], "%Y-%m-%d") < end_dt]
        
        # Apply event type filter
        if event_types_filter:
            types = [t.strip().lower() for t in event_types_filter.split(",")]
            events = [e for e in events if any(t in (e.get("event_type") or "").lower() for t in types)]
        
        # Apply severity filter
        if severity_filter:
            severities = [s.strip().upper() for s in severity_filter.split(",")]
            events = [e for e in events if (e.get("severity") or "LOW").upper() in severities]
        
        # Apply camera filter
        if cameras_filter:
            cameras = [c.strip() for c in cameras_filter.split(",")]
            events = [e for e in events if (e.get("camera") or "") in cameras]
        
        total_incidents = len(events)
        people = sum(1 for e in events if "person" in (e.get("event_type") or "").lower())
        vehicles = sum(1 for e in events if "vehicle" in (e.get("event_type") or "").lower())
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
            "total": 0,
            "people": 0,
            "vehicles": 0,
            "threat": "UNKNOWN",
            "labels": [],
            "values": [],
            "falls": 0,
            "weapons": 0,
            "events": []
        }), 200


@app.route("/reports_data")
def reports_data():
    """Returns structured report data for the reports page."""
    try:
        from services.report_service import ReportService
        data = ReportService.generate_summary_data(timeframe="daily")
        
        from database.db import get_all_cameras
        cameras = get_all_cameras(user_id=_get_user_id())
        
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
        
        evidence_count = 0
        evidence_today = 0
        try:
            from database.db import get_all_evidence
            ev = get_all_evidence(limit=500, user_id=_get_user_id())
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
            "evidence": {
                "images": evidence_count,
                "today": evidence_today,
                "storage": f"{storage_mb} MB"
            },
            "high_priority": high_priority
        }), 200
    except Exception as e:
        return jsonify({
            "camera_online": 0,
            "total_events": 0,
            "total_evidence": 0,
            "threat_level": "LOW",
            "event_summary": [],
            "camera_summary": [],
            "evidence": {"images": 0, "today": 0, "storage": "0 MB"},
            "high_priority": []
        }), 200


@app.route("/download_csv")
def download_csv():
    """Generates and downloads a CSV report."""
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
    """PDF export is handled client-side via printable HTML report.
    This endpoint provides a redirect hint for direct URL access."""
    return jsonify({
        "success": False,
        "error": "PDF export is generated from the Reports page. Use the Export PDF button.",
        "hint": "Navigate to /reports and click the Export PDF button."
    }), 200


@app.route("/api/settings", methods=["GET", "POST"])
@require_auth
@require_csrf  # <-- CSRF Protection Added Here
@rate_limit
def api_settings():
    user_id = _get_user_id()
    if request.method == "GET":
        settings = SettingsStore.get_all_settings(user_id=user_id)
        return jsonify(settings)
    else:
        data = request.get_json(silent=True) or {}
        key = data.get("key")
        value = data.get("value")
        if key is None:
            return jsonify({"success": False, "error": "Missing 'key'"}), 400
        success = SettingsStore.set_setting(key, value, user_id=user_id)
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
    results = SettingsStore.save_camera_settings(cameras, user_id=_get_user_id())
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
    success = SettingsStore.set_setting("notifications", notifications, user_id=_get_user_id())
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
    """Serves stored evidence screenshots using project-root-relative path."""
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


# ==========================================
# AUTO-START CAMERAS FROM CONFIG
# ==========================================
def _auto_start_cameras():
    """Start cameras from CAMERAS config (including VIDEO_FILE if set)."""
    from config import CAMERAS

    if not CAMERAS:
        return
    for cam_config in CAMERAS:
        name = cam_config["name"]
        source = cam_config["source"]
        zone = cam_config.get("zone", "General Area")
        # Parse source: digit → int (webcam index), else string (file/URL)
        if str(source).isdigit():
            ip_url = int(source)
        else:
            ip_url = source
        try:
            camera_manager.add_camera(
                name=name,
                ip_url=ip_url,
                zone=zone,
                auto_start=True
            )
            print(f"✔ Auto-started camera: {name} ({zone})")
        except Exception as e:
            print(f"⚠️ Failed to auto-start camera {name}: {e}")

try:
    _auto_start_cameras()
except Exception as e:
    print(f"⚠️ Camera auto-start notice: {e}")


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")
    app.run(host="127.0.0.1", port=5000, debug=debug_mode)