import os
import cv2
import gzip
import time
import json
import logging
import secrets
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from flask import Flask, render_template, jsonify, Response, send_from_directory, send_file, request, session, redirect, url_for

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Sentinel-X Core & AI Imports ---
from core.system_monitor import SystemMonitor
from ai.health import AIHealthMonitor
from ai.queue_manager import DetectionQueueManager
from ai.inference import YOLOInferenceEngine
from ai.worker import YOLOWorker
from core.recovery import AutoRecoveryManager

# --- Authentication ---
from api.auth import (
    is_authenticated, login, logout, signup, direct_signup,
    get_csrf_token, validate_csrf_token,
    require_auth, require_csrf, rate_limit,
    get_current_user_id,
    request_verification_code, verify_and_complete_signup
)


def _get_user_id():
    """Get the current user ID from session, defaulting to 1 for backward compatibility."""
    return get_current_user_id()

# --- Camera Subsystem Import ---
from camera.camera_manager import camera_manager

# --- Database & Dashboard Imports ---
from database.db import db_connection, db_write_connection, get_all_events
from dashboard.store import get_events, get_stats
from dashboard.timeline import get_timeline
from dashboard.settings_store import SettingsStore

# SocketIO Import
try:
    from services.socket_manager import socketio
except Exception:
    # The previous fallback re-imported flask_socketio, so it failed for exactly
    # the same reason and a missing dependency turned into an ImportError during
    # app startup. Degrade to a no-op stub instead: realtime updates are
    # optional, the REST API and MJPEG feeds are not.
    class _NullSocketIO:
        """Stand-in used when flask-socketio is unavailable."""

        def __init__(self, *args, **kwargs):
            pass

        def init_app(self, app, *args, **kwargs):
            pass

        def emit(self, *args, **kwargs):
            pass

        def on(self, *args, **kwargs):
            def decorator(fn):
                return fn
            return decorator

        def run(self, *args, **kwargs):
            pass

    socketio = _NullSocketIO()
    print("SocketIO unavailable; realtime push disabled (REST + MJPEG still work).")

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Static assets are versioned with ?v=<stamp>, so they can be cached hard.
# 0 meant every stylesheet and script was re-downloaded on every page view.
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 31536000
app.secret_key = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))

# --- Response compression -------------------------------------------------
# The UI ships ~378 KB of CSS and ~350 KB of JS as separate render-blocking
# files. Compressing them cuts that to roughly a tenth without touching the
# cascade, which is far safer than hand-minifying the stylesheets.
# Streaming media (MJPEG) is deliberately excluded: compressing it would
# buffer an endless response and stall every feed.
_COMPRESSIBLE = (
    "text/html", "text/css", "text/javascript", "application/javascript",
    "application/json", "image/svg+xml", "text/plain",
)
_COMPRESS_MIN_BYTES = 1024


@app.after_request
def compress_response(response):
    try:
        ctype = (response.headers.get("Content-Type") or "").split(";")[0].strip()
        if ctype not in _COMPRESSIBLE:
            return response
        # Never re-encode a body a handler already compressed, and never touch
        # a streamed response (no Content-Length and Transfer-Encoding chunked).
        if response.headers.get("Content-Encoding"):
            return response
        if response.headers.get("Transfer-Encoding"):
            return response
        if "gzip" not in (request.headers.get("Accept-Encoding") or "").lower():
            return response

        data = response.get_data() if not response.direct_passthrough else None
        if data is None:
            # send_file() marks its response direct_passthrough, which means the
            # body has not been read yet. Materialise it so the stylesheets and
            # scripts actually get compressed.
            response.direct_passthrough = False
            data = response.get_data()
        if len(data) < _COMPRESS_MIN_BYTES:
            return response

        compressed = gzip.compress(data, compresslevel=6)
        # Only use it when it actually helps.
        if len(compressed) >= len(data):
            return response

        response.set_data(compressed)
        response.headers["Content-Encoding"] = "gzip"
        response.headers["Content-Length"] = str(len(compressed))
        response.headers.add("Vary", "Accept-Encoding")
        return response
    except Exception:  # pragma: no cover - never fail a response over encoding
        return response


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
from config import MODEL_PATH as _MODEL_PATH, MAX_QUEUE_SIZE as _MAX_QUEUE_SIZE

sys_monitor = SystemMonitor()
ai_health = AIHealthMonitor(max_queue_size=_MAX_QUEUE_SIZE)
# Use the configured capacity so the health monitor's ceiling matches reality.
queue_mgr = DetectionQueueManager(maxsize=_MAX_QUEUE_SIZE)
engine = YOLOInferenceEngine(model_path=_MODEL_PATH, health_monitor=ai_health)

worker = YOLOWorker(queue_mgr, engine, ai_health)
recovery = AutoRecoveryManager(ai_health, queue_mgr, engine, check_interval=0.5)
recovery.attach_worker(worker)

# Start Background Threads
_pipeline_started = False


def start_background_services():
    """Starts the AI worker, recovery engine and detection loop exactly once.

    Importing this module used to start the worker/recovery pair immediately
    while ``main.py --flask`` and the Docker/gunicorn entrypoints never started
    ``core.engine.run_engine`` at all -- so those deployments served a dashboard
    that could never produce detections, events or evidence. Every entrypoint
    now calls this instead of relying on import side effects.

    This is an explicit request, so it always starts. Use
    ``autostart_background_services()`` for the import-time behaviour, which
    honours ``SENTINELX_AUTOSTART=0``.
    """
    global _pipeline_started
    if _pipeline_started:
        return False

    _pipeline_started = True
    try:
        worker.start()
        recovery.start()
        print("Sentinel-X AI Worker & Recovery Engine Active")
    except Exception as e:
        print(f"Pipeline start notice: {e}")

    try:
        import threading

        from core.engine import run_engine

        event_user_id = int(os.getenv("SENTINELX_USER_ID", "1"))
        stop_event = threading.Event()
        app.config["SENTINELX_STOP_EVENT"] = stop_event
        thread = threading.Thread(
            target=run_engine,
            kwargs={"user_id": event_user_id, "stop_event": stop_event},
            name="sentinelx-engine",
            daemon=True,
        )
        thread.start()
        app.config["SENTINELX_ENGINE_THREAD"] = thread
        print("Sentinel-X detection engine started")
    except Exception as e:
        print(f"Detection engine start notice: {e}")
    return True


def autostart_background_services():
    """Import-time startup. Honours SENTINELX_AUTOSTART=0 to stay import-safe.

    Tests and WSGI setups that call start_background_services() themselves set
    SENTINELX_AUTOSTART=0 so importing the module has no side effects.
    """
    if os.getenv("SENTINELX_AUTOSTART", "1") == "0":
        return False
    return start_background_services()


try:
    autostart_background_services()
except Exception as e:
    print(f"Pipeline autostart notice: {e}")


# ==========================================
# DATABASE INITIALIZATION FOR FACES
# ==========================================
def _init_face_table():
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS known_faces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    image_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            print("✔ Initialized known_faces table")
    except Exception as e:
        print(f"⚠️ Face table init notice: {e}")

_init_face_table()


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
    os.makedirs('logs', exist_ok=True)
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


@app.route("/api/auth/signup/request-code", methods=["POST"])
@rate_limit
def api_signup_request_code():
    """Deprecated: direct signup is now used instead."""
    return jsonify({
        "status": "error",
        "message": "Email verification is no longer required. Please use the signup form."
    }), 400


@app.route("/api/auth/signup", methods=["POST"])
@rate_limit
def api_signup():
    """Create account immediately without email verification and auto-login."""
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")
    email = data.get("email", "")

    if not all(isinstance(x, str) for x in (username, password, email)):
        return jsonify({"status": "error", "message": "Invalid request format"}), 400
    if len(username) > 100 or len(password) > 100 or len(email) > 200:
        return jsonify({"status": "error", "message": "Request too large"}), 400

    success, result = direct_signup(username, password, email)
    if success:
        login(username, password)
        return jsonify({
            "status": "success",
            "message": "Account created successfully. Welcome to Sentinel-X!",
            "redirect": "/"
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


@app.context_processor
def _inject_csrf():
    """Expose csrf_token() to every template.

    base.html renders it into a meta tag so the JS wrapper can attach the
    header synchronously, without waiting on an extra round trip.
    """
    try:
        return {"csrf_token": get_csrf_token}
    except Exception:  # pragma: no cover - outside a request context
        return {"csrf_token": lambda: ""}


# ==========================
# ROUTE PROTECTION
# ==========================

_PUBLIC_ENDPOINTS = frozenset({
    "landing_page", "login_page", "signup_page", "static",
    "api_login", "api_signup_request_code", "api_signup", "api_auth_status",
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
        return  

    if ep in _PUBLIC_ENDPOINTS:
        return
    for prefix in _PUBLIC_PREFIXES:
        if ep.startswith(prefix + "."):
            return

    if not is_authenticated():
        if request.path.startswith("/api/") or \
           request.path.startswith("/video_feed") or \
           request.path.startswith("/download_") or \
           request.path.startswith("/evidence/screenshots") or \
           request.path in ("/events", "/stats", "/timeline",
                            "/gallery", "/ai_summary",
                            "/analytics_data", "/reports_data"):
            return jsonify({"error": "Authentication required",
                            "status": "unauthorized"}), 401
        return redirect(url_for("login_page"))


# ==========================
# LOGIN PAGE
# ==========================

@app.route("/login")
def login_page():
    if is_authenticated():
        return redirect(url_for("dashboard_page"))
    return render_template("login.html")


@app.route("/signup")
def signup_page():
    if is_authenticated():
        return redirect(url_for("dashboard_page"))
    return render_template("signup.html")


# ==========================
# PAGE ROUTES (UI VIEWS)
# ==========================
@app.route("/")
def landing_page():
    return render_template("landing.html")


@app.route("/dashboard")
def dashboard_page():
    return render_template("index.html")

@app.route("/cameras")
def cameras():
    return render_template("cameras.html")

@app.route("/camera_view")
def camera_view():
    camera_name = request.args.get('camera', 'Camera_01')

    from camera.camera_manager import camera_manager
    pipeline = camera_manager.get_pipeline(camera_name)
    if not pipeline:
        available = list(camera_manager.pipelines.keys())
        if available:
            camera_name = available[0]
        else:
            camera_name = 'Camera_01'
    
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

@app.route("/cameras_wall")
def cameras_wall():
    return render_template("cameras_wall.html")

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


_COPILOT_HELP = (
    "Ask about: incidents today, high severity alerts, busiest cameras, "
    "offline cameras, system health, storage usage, or detection trends."
)


def _copilot_answer(question, user_id):
    """Answers operator questions from live system data.

    This is a deterministic analyst over the same metrics the dashboard shows
    (it is not a language model). It previously returned a hardcoded
    "integration pending" string for every question.
    """
    from database.db import get_all_cameras, get_event_stats, get_all_events

    q = (question or "").lower()
    totals = get_event_stats(user_id=user_id)
    cameras = get_all_cameras(user_id=user_id)
    online = [c for c in cameras if (c.get("status") or "").upper() == "ONLINE"]
    offline = [c for c in cameras if c not in online]

    def wants(*keywords):
        return any(k in q for k in keywords)

    if wants("help", "what can you"):
        return _COPILOT_HELP

    if wants("offline", "down", "not working", "disconnected"):
        if not offline:
            return "All %d registered cameras are online." % len(cameras)
        return "Offline cameras (%d): %s" % (
            len(offline), ", ".join(sorted(c.get("name", "?") for c in offline)))

    if wants("online", "camera status", "how many cameras"):
        return "%d of %d cameras online (%s%%)." % (
            len(online), len(cameras),
            round(100.0 * len(online) / len(cameras)) if cameras else 0)

    if wants("camera") and wants("busy", "most", "active"):
        recent = get_all_events(limit=500, user_id=user_id)
        counts = {}
        for e in recent:
            counts[e.get("camera", "Unknown")] = counts.get(e.get("camera", "Unknown"), 0) + 1
        if not counts:
            return "No recent events recorded yet."
        top = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:3]
        return "Most active cameras in the last %d events: %s." % (
            len(recent), ", ".join("%s (%d)" % (name, n) for name, n in top))

    if wants("high", "critical", "severe", "alert", "threat"):
        high = int(totals.get("high_sev", 0) or 0)
        if not high:
            return "No high or critical severity events recorded."
        level = "CRITICAL" if high > 5 else "MEDIUM"
        return ("%d high/critical severity events recorded - current threat level is %s. "
                "Review the incident center for detail." % (high, level))

    if wants("storage", "disk", "space"):
        from flask import current_app
        total = 0
        screenshots_dir = os.path.join(PROJECT_ROOT, "evidence", "screenshots")
        if os.path.isdir(screenshots_dir):
            for dirpath, _dirs, files in os.walk(screenshots_dir):
                for f in files:
                    try:
                        total += os.path.getsize(os.path.join(dirpath, f))
                    except OSError:
                        pass
        return "Evidence storage in use: %.2f MB." % (total / (1024 * 1024))

    if wants("health", "system", "cpu", "ram", "performance", "status"):
        sys_stats = sys_monitor.get_stats()
        ai_stats = ai_health.get_health_status()
        return ("CPU %.1f%%, RAM %.1f%%, disk %.1f%%. AI engine: %s (detection FPS %s, "
                "queue %s/%s)." % (
                    sys_stats.get("cpu_usage_percent", 0),
                    sys_stats.get("ram_usage_percent", 0),
                    sys_stats.get("disk_usage_percent", 0),
                    ai_stats.get("status", "unknown"),
                    ai_stats.get("metrics", {}).get("detection_fps", 0),
                    ai_stats.get("metrics", {}).get("queue_size", 0),
                    ai_stats.get("metrics", {}).get("queue_capacity_percent", 0) and ai_health.max_queue_size,
                ))

    # Default: a factual snapshot rather than a canned string.
    return ("%d events recorded (avg confidence %.1f%%): %d persons, %d vehicles, "
            "%d high severity. Cameras: %d/%d online. %s" % (
                totals.get("total", 0),
                float(totals.get("avg_confidence", 0)) * 100,
                totals.get("person_events", 0),
                totals.get("vehicle_events", 0),
                totals.get("high_sev", 0),
                len(online), len(cameras),
                _COPILOT_HELP))


@app.route("/api/copilot", methods=["POST"])
@require_auth
@require_csrf
def api_copilot():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"response": "Please ask a question.", "status": "error"}), 400
    if len(question) > 500:
        question = question[:500]
    try:
        return jsonify({
            "response": _copilot_answer(question, _get_user_id()),
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({"response": "Unable to answer right now.", "status": "error",
                        "error": str(e)}), 500


@app.route("/settings")
def settings():
    return render_template("settings.html")


# ==========================
# FACE REGISTRATION ROUTE
# ==========================
@app.route("/register_face", methods=["GET", "POST"])
@require_auth
@require_csrf
def register_face():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        file = request.files.get("face_image")
        if file and name:
            filename = f"{secure_filename(name)}_{int(time.time())}.jpg"
            faces_dir = os.path.join(PROJECT_ROOT, "dashboard", "static", "faces")
            os.makedirs(faces_dir, exist_ok=True)
            filepath = os.path.join(faces_dir, filename)
            file.save(filepath)
            stored_path = os.path.relpath(filepath, PROJECT_ROOT).replace("\\", "/")

            try:
                with db_write_connection() as conn:
                    conn.execute(
                        "INSERT INTO known_faces (user_id, name, image_path) VALUES (?, ?, ?)",
                        (_get_user_id(), name, stored_path)
                    )
            except Exception as e:
                print(f"Failed to save face to DB: {e}")
            return redirect(url_for("cameras"))
    return render_template("register_face.html")


# ==========================
# LIVE STREAM GENERATORS
# ==========================
from dashboard.stream import generate as stream_generate

def generate_camera_stream(camera_name="Camera_01"):
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
    camera_name = request.args.get('camera_name', 'Camera_01')
    return Response(generate_camera_stream(camera_name), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/events")
def events():
    """Recent events for the current user.

    Honours the limit and date filters the UI sends; previously all three query
    parameters were ignored and every response was the same default page.
    """
    limit = max(1, min(request.args.get("limit", 20, type=int) or 20, 2000))
    start_date = request.args.get("start_date") or None
    end_date = request.args.get("end_date") or None
    event_types = [t for t in (request.args.get("event_type") or "").split(",") if t] or None
    severities = [s for s in (request.args.get("severity") or "").split(",") if s] or None
    cameras = [c for c in (request.args.get("camera") or "").split(",") if c] or None

    return jsonify(get_all_events(
        limit=limit,
        user_id=_get_user_id(),
        start_date=start_date,
        end_date=end_date,
        event_types=event_types,
        severities=severities,
        cameras=cameras,
    ))


@app.route("/stats")
def stats():
    return jsonify(get_stats(user_id=_get_user_id()))


@app.route("/timeline")
def timeline():
    return {"timeline": get_timeline(user_id=_get_user_id())}


@app.route("/api/storage")
def api_storage():
    total_size = 0
    screenshots_dir = os.path.join(PROJECT_ROOT, "evidence", "screenshots")
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
    try:
        user_id = _get_user_id()
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM evidence WHERE user_id = ? ORDER BY id DESC LIMIT 50", (user_id,))
            rows = cursor.fetchall()
            return jsonify([dict(row) for row in rows]), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/ai_summary")
def ai_summary_endpoint():
    try:
        from dashboard.store import get_stats
        from database.db import get_event_stats
        user_id = _get_user_id()
        stats = get_stats(user_id=user_id)
        totals = get_event_stats(user_id=user_id)
        risk = "LOW"
        if stats.get("high_severity_incidents", 0) > 5:
            risk = "HIGH"
        elif stats.get("high_severity_incidents", 0) > 0:
            risk = "MEDIUM"
        # get_stats() never returned 'accuracy'/'avg_confidence', so this
        # expression always fell through to the hardcoded 92.5.
        confidence_pct = round(float(totals.get("avg_confidence", 0.0)) * 100, 1)
        return jsonify({
            "risk": risk,
            "detections": stats.get("total_incidents", 0),
            "persons": stats.get("persons", 0),
            "vehicles": stats.get("vehicles", 0),
            "confidence": f"{min(confidence_pct, 100):.1f}%",
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
@require_auth
def api_health_status():
    return jsonify({
        "system": sys_monitor.get_stats(),
        "ai_engine": ai_health.get_health_status(),
        "recovery_restarts": recovery.restart_count
    })


@app.route("/api/demo/scenarios", methods=["GET"])
@require_auth
def api_demo_scenarios():
    from events.demo_controller import demo_controller
    return jsonify({
        "scenarios": list(demo_controller.scenarios.keys())
    }), 200


@app.route("/api/demo/trigger", methods=["POST"])
@require_auth
@require_csrf
def api_demo_trigger():
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
    try:
        from dashboard.store import get_stats, get_events
        from database.db import get_all_evidence
        from collections import Counter
        from datetime import datetime, timedelta
        
        user_id = _get_user_id()

        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        event_types_filter = request.args.get("event_types")
        severity_filter = request.args.get("severity")
        cameras_filter = request.args.get("cameras")

        stats = get_stats(user_id=user_id)

        # Filtering happens in SQL rather than on a truncated page of rows:
        # get_events() ignores `limit`, so "the last 500 events" were actually
        # the last 20, and any date/type filter applied to that small slice.
        events = get_all_events(
            limit=2000,
            user_id=user_id,
            start_date=("%s 00:00:00" % start_date) if start_date else None,
            end_date=("%s 00:00:00" % end_date) if end_date else None,
            event_types=[t.strip() for t in event_types_filter.split(",")] if event_types_filter else None,
            severities=[s.strip() for s in severity_filter.split(",")] if severity_filter else None,
            cameras=[c.strip() for c in cameras_filter.split(",")] if cameras_filter else None,
        )

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
            "total": 0, "people": 0, "vehicles": 0, "threat": "UNKNOWN",
            "labels": [], "values": [], "falls": 0, "weapons": 0, "events": []
        }), 200


@app.route("/reports_data")
def reports_data():
    try:
        from services.report_service import ReportService, TIMEFRAME_DAYS
        # The Reports page sends the selected period; it was hardcoded to
        # "daily", so weekly/monthly selectors never changed the numbers.
        requested = (request.args.get("timeframe") or "daily").lower()
        timeframe = requested if requested in TIMEFRAME_DAYS else "daily"
        user_id = _get_user_id()
        data = ReportService.generate_summary_data(timeframe=timeframe, user_id=user_id)
        
        from database.db import get_all_cameras
        cameras = get_all_cameras(user_id=_get_user_id())
        
        event_summary = [{"name": name, "count": count} for name, count in data.get("breakdown_by_type", {}).items()]
        camera_summary = [{"name": cam.get("name", "Unknown"), "status": cam.get("status", "OFFLINE"), "events": cam.get("event_count", 0)} for cam in cameras]
        
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
            screenshots_dir = os.path.join(PROJECT_ROOT, "evidence", "screenshots")
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
            "timeframe": timeframe,
            "event_summary": event_summary,
            "camera_summary": camera_summary,
            "evidence": {"images": evidence_count, "today": evidence_today, "storage": f"{storage_mb} MB"},
            "high_priority": high_priority
        }), 200
    except Exception as e:
        return jsonify({
            "camera_online": 0, "total_events": 0, "total_evidence": 0, "threat_level": "LOW",
            "event_summary": [], "camera_summary": [], "evidence": {"images": 0, "today": 0, "storage": "0 MB"}, "high_priority": []
        }), 200


@app.route("/download_csv")
def download_csv():
    try:
        from services.report_service import ReportService, TIMEFRAME_DAYS
        requested = (request.args.get("timeframe") or "daily").lower()
        timeframe = requested if requested in TIMEFRAME_DAYS else "daily"
        csv_data = ReportService.generate_csv_report(
            timeframe=timeframe, user_id=_get_user_id()
        )
        filename = "sentinelx_report_%s.csv" % timeframe
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=%s" % filename}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/download_pdf")
def download_pdf():
    return jsonify({
        "success": False,
        "error": "PDF export is generated from the Reports page. Use the Export PDF button.",
        "hint": "Navigate to /reports and click the Export PDF button."
    }), 200


@app.route("/api/settings", methods=["GET", "POST"])
@require_auth
@require_csrf
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
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM evidence WHERE timestamp < ?", (cutoff,))
            deleted = cursor.rowcount
            conn.commit()
        return jsonify({"success": True, "deleted": deleted}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/evidence/screenshots/<path:filename>")
def evidence_screenshot(filename):
    """Serves stored evidence screenshots securely preventing path traversal."""
    evidence_dir = os.path.abspath(os.path.join(app.root_path, "..", "evidence", "screenshots"))

    # Sanitize and extract base filename to avoid directory traversal
    safe_name = secure_filename(os.path.basename(filename))
    if not safe_name:
        return jsonify({"error": "Invalid filename"}), 400

    return send_from_directory(evidence_dir, safe_name)


# ==========================================
# AUTO-START CAMERAS FROM CONFIG
# ==========================================
def _auto_start_cameras():
    from config import CAMERAS

    if not CAMERAS:
        return
    for cam_config in CAMERAS:
        name = cam_config["name"]
        source = cam_config["source"]
        zone = cam_config.get("zone", "General Area")
        
        # Skip video file sources - they are handled by the evidence video watcher
        if not str(source).isdigit() and not str(source).startswith(("rtsp://", "rtsps://", "http://", "https://")):
            if os.path.isfile(str(source)):
                print(f"[AutoStart] Skipping video-file camera '{name}' - handled by evidence watcher")
                continue
        
        if str(source).isdigit():
            ip_url = int(source)
        else:
            ip_url = source
        try:
            camera_manager.add_camera(
                name=name,
                ip_url=ip_url,
                zone=zone,
                auto_start=True,
                skip_worker=True,
            )
            print(f"✔ Auto-started camera: {name} ({zone})")
        except Exception as e:
            print(f"⚠️ Failed to auto-start camera {name}: {e}")


def _register_existing_video_evidence():
    """Register any existing video files in evidence/videos as cameras."""
    try:
        watcher = camera_manager._video_watcher
        if not watcher:
            return
        existing = watcher.initial_scan()
        for filepath in existing:
            print(f"✔ Registered existing evidence video: {os.path.basename(filepath)}")
    except Exception as e:
        print(f"⚠️ Existing video evidence registration notice: {e}")


def _start_camera_health_monitor():
    """Start a background thread that monitors camera health and removes failed cameras."""
    import threading
    import time
    
    def monitor_loop():
        while True:
            try:
                time.sleep(30)  # Check every 30 seconds
                if not camera_manager:
                    continue
                
                # Get all pipelines
                pipelines = dict(camera_manager.pipelines)
                for name, pipeline in list(pipelines.items()):
                    # Skip evidence cameras - they loop and are stable
                    if name.startswith("Evidence_"):
                        continue
                    
                    # Check if camera has been failing for too long
                    stream = pipeline.stream
                    if stream and hasattr(stream, 'reconnects') and stream.reconnects > 10:
                        print(f"[HealthMonitor] Removing failed camera: {name} (reconnects={stream.reconnects})")
                        camera_manager.remove_camera(name)
                    elif stream and stream.status in ["OFFLINE", "CRITICAL", "ERROR"]:
                        # Check if it's been in bad state for a while
                        if hasattr(stream, '_last_error_time'):
                            if time.time() - stream._last_error_time > 120:  # 2 minutes
                                print(f"[HealthMonitor] Removing stale camera: {name} (status={stream.status})")
                                camera_manager.remove_camera(name)
                        else:
                            stream._last_error_time = time.time()
            except Exception as e:
                print(f"[HealthMonitor] Error: {e}")
    
    thread = threading.Thread(target=monitor_loop, daemon=True)
    thread.start()
    print("✔ Camera health monitor started")


_camera_services_started = False


def start_camera_services():
    """Starts the camera pipelines and background watchers exactly once.

    Cameras are registered with ``skip_worker=True`` because the detection loop
    in ``core.engine`` owns inference for every pipeline; starting a per-camera
    worker here as well would run inference twice on the same frames.

    This is an explicit request, so it always starts. See
    ``autostart_camera_services()`` for the import-time behaviour.
    """
    global _camera_services_started
    if _camera_services_started:
        return False
    _camera_services_started = True

    try:
        _auto_start_cameras()
        _register_existing_video_evidence()
        camera_manager.start_video_watcher()
        _start_camera_health_monitor()
    except Exception as e:
        print(f"Camera auto-start notice: {e}")
    return True


def autostart_camera_services():
    """Import-time camera startup. Honours SENTINELX_AUTOSTART=0."""
    if os.getenv("SENTINELX_AUTOSTART", "1") == "0":
        return False
    return start_camera_services()


try:
    autostart_camera_services()
except Exception as e:
    print(f"Camera auto-start notice: {e}")


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")
    app.run(host="127.0.0.1", port=5000, debug=debug_mode)
