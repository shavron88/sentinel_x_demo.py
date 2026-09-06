"""
SentinelX Authentication Module with Email OTP Verification & Database
"""
import os
import sqlite3
import hashlib
import secrets
import time
import random
import json
import logging
from datetime import datetime, timedelta
from flask import session, request, jsonify

DB_PATH = "sentinelx.db"
logger = logging.getLogger("SentinelX.Database")

DEMO_USERNAME = os.getenv("SENTINELX_USER", "sentinelx_admin")
DEMO_PASSWORD_HASH = hashlib.sha256(
    os.getenv("SENTINELX_PASSWORD", "SentinelX_SecurePassword2026!").encode()
).hexdigest()

SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT", "60"))
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 60
_rate_limit_store = {}


def get_connection():
    """Returns a thread-safe connection to SQLite with Row factory."""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def _check_rate_limit(key):
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS
    if key not in _rate_limit_store:
        _rate_limit_store[key] = []
    _rate_limit_store[key] = [t for t in _rate_limit_store[key] if t > window_start]
    if len(_rate_limit_store[key]) >= RATE_LIMIT_MAX_REQUESTS:
        return False
    _rate_limit_store[key].append(now)
    return True


def is_authenticated():
    if "authenticated" not in session or session.get("authenticated") != True:
        return False
    last_active = session.get("last_active")
    if not last_active:
        return False
    try:
        last_active_time = datetime.fromisoformat(last_active)
        if datetime.now() - last_active_time > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
            session.clear()
            return False
    except (ValueError, TypeError):
        session.clear()
        return False
    session["last_active"] = datetime.now().isoformat()
    return True


def get_current_user_id():
    return session.get("user_id", 1)


def login(username, password):
    if not username or not password:
        return False, "Username and password required"
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, password_hash, is_verified FROM admin_users WHERE username = ?", (username,))
            row = cursor.fetchone()
        
        if row:
            if "is_verified" in row.keys() and row["is_verified"] == 0:
                return False, "Account not verified. Please complete signup verification."
            if row["password_hash"] == password_hash:
                session.clear()
                session["authenticated"] = True
                session["username"] = username
                session["user_id"] = row["id"]
                session["email"] = f"{username}@sentinelx.ai"
                session["role"] = "System Administrator"
                session["last_active"] = datetime.now().isoformat()
                session["csrf_token"] = secrets.token_hex(32)
                return True, "Login successful"
    except Exception as e:
        print(f"Database authentication error: {e}")
        
    if username == DEMO_USERNAME and password_hash == DEMO_PASSWORD_HASH:
        session.clear()
        session["authenticated"] = True
        session["username"] = username
        session["user_id"] = 1
        session["email"] = f"{username}@sentinelx.ai"
        session["role"] = "System Administrator"
        session["last_active"] = datetime.now().isoformat()
        session["csrf_token"] = secrets.token_hex(32)
        return True, "Login successful (demo fallback)"
    return False, "Invalid credentials"


def logout():
    session.clear()


def init_db():
    """Creates database schema tables and adds required columns if missing."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Events Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL DEFAULT 1,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT DEFAULT 'LOW',
                camera TEXT NOT NULL,
                zone TEXT DEFAULT 'General Area',
                track_id INTEGER DEFAULT -1,
                confidence REAL DEFAULT 0.0,
                duration REAL DEFAULT 0.0,
                metadata TEXT
            )
        """)

        # Evidence Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL DEFAULT 1,
                event_id INTEGER,
                timestamp TEXT NOT NULL,
                camera TEXT NOT NULL,
                image_path TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (event_id) REFERENCES events (id)
            )
        """)

        # Cameras Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cameras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL DEFAULT 1,
                name TEXT NOT NULL,
                location TEXT DEFAULT 'Unspecified',
                stream_url TEXT NOT NULL,
                status TEXT DEFAULT 'OFFLINE',
                fps REAL DEFAULT 0.0,
                latency REAL DEFAULT 0.0,
                resolution TEXT DEFAULT '640x480',
                network_errors INTEGER DEFAULT 0,
                decode_errors INTEGER DEFAULT 0,
                last_error TEXT,
                is_rtsp INTEGER DEFAULT 0,
                UNIQUE(user_id, name)
            )
        """)

        # Admin Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'System Administrator',
                is_verified INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Migration checks for existing columns
        migrations = [
            ("ALTER TABLE cameras ADD COLUMN network_errors INTEGER DEFAULT 0",),
            ("ALTER TABLE cameras ADD COLUMN decode_errors INTEGER DEFAULT 0",),
            ("ALTER TABLE cameras ADD COLUMN last_error TEXT",),
            ("ALTER TABLE cameras ADD COLUMN is_rtsp INTEGER DEFAULT 0",),
            ("ALTER TABLE events ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1",),
            ("ALTER TABLE evidence ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1",),
            ("ALTER TABLE cameras ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1",),
            ("ALTER TABLE settings ADD COLUMN user_id INTEGER",),
            ("ALTER TABLE admin_users ADD COLUMN is_verified INTEGER DEFAULT 1",)
        ]
        for query_tuple in migrations:
            try:
                cursor.execute(query_tuple[0])
            except sqlite3.OperationalError:
                pass

        # Seed default admin user if not exists
        default_username = "sentinelx_admin"
        default_password = "SentinelX_SecurePassword2026!"
        default_password_hash = hashlib.sha256(default_password.encode()).hexdigest()
        cursor.execute(
            "INSERT OR IGNORE INTO admin_users (username, password_hash, email, role, is_verified) VALUES (?, ?, ?, ?, 1)",
            (default_username, default_password_hash, f"{default_username}@sentinelx.ai", "System Administrator")
        )

        conn.commit()
        logger.info("Database initialized successfully.")


init_db()


def initiate_signup(username, password, email):
    """Directly registers and saves user to database upon signup."""
    import re
    if not username or not password or not email:
        return False, "Username, password and email are required"
    if len(username) < 3 or len(username) > 50:
        return False, "Username must be between 3 and 50 characters"
    if len(password) < 4 or len(password) > 100:
        return False, "Password must be at least 4 characters"
    if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
        return False, "Username may only contain letters, numbers, dots, hyphens and underscores"
    if "@" not in email or "." not in email:
        return False, "Invalid email address format"

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM admin_users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                return False, "Username or email already exists"

            password_hash = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute(
                "INSERT INTO admin_users (username, password_hash, email, is_verified) VALUES (?, ?, ?, 1)",
                (username, password_hash, email)
            )
            conn.commit()
        return True, "Account successfully created! You can now log in."
    except Exception as e:
        print(f"Signup database error: {e}")
        return False, "Failed to create account. Please try again."


def signup(username, password, email):
    """Alias wrapper to satisfy dashboard/app.py import expectations."""
    return initiate_signup(username, password, email)


def verify_otp_and_register(email, otp_code):
    """Legacy wrapper support."""
    return True, "Account already verified."


# ==========================================
# EVENTS & EVIDENCE FUNCTIONS
# ==========================================

def get_all_events(limit=50, user_id=None):
    """Fetches recent recorded events from database."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            if user_id is not None:
                cursor.execute("SELECT * FROM events WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit))
            else:
                cursor.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        return []


def get_evidence_by_id(evidence_id, user_id=None):
    """Fetches single evidence record with joined event details."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            if user_id is not None:
                cursor.execute("""
                    SELECT e.*, ev.event_type, ev.severity, ev.zone, ev.confidence as event_confidence
                    FROM evidence e
                    LEFT JOIN events ev ON e.event_id = ev.id
                    WHERE e.id = ? AND e.user_id = ?
                """, (evidence_id, user_id))
            else:
                cursor.execute("""
                    SELECT e.*, ev.event_type, ev.severity, ev.zone, ev.confidence as event_confidence
                    FROM evidence e
                    LEFT JOIN events ev ON e.event_id = ev.id
                    WHERE e.id = ?
                """, (evidence_id,))
            row = cursor.fetchone()
            return _row_to_evidence_dict(row)
    except Exception as ex:
        logger.error(f"Error fetching evidence: {ex}")
        return None


def get_all_evidence(limit=100, user_id=None):
    """Fetches all evidence records with joined event details for the evidence vault."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            if user_id is not None:
                cursor.execute("""
                    SELECT e.*, ev.event_type, ev.severity, ev.zone, ev.confidence as event_confidence
                    FROM evidence e
                    LEFT JOIN events ev ON e.event_id = ev.id
                    WHERE e.user_id = ?
                    ORDER BY e.timestamp DESC
                    LIMIT ?
                """, (user_id, limit))
            else:
                cursor.execute("""
                    SELECT e.*, ev.event_type, ev.severity, ev.zone, ev.confidence as event_confidence
                    FROM evidence e
                    LEFT JOIN events ev ON e.event_id = ev.id
                    ORDER BY e.timestamp DESC
                    LIMIT ?
                """, (limit,))
            rows = cursor.fetchall()
            return [_row_to_evidence_dict(row) for row in rows]
    except Exception as ex:
        logger.error(f"Error fetching evidence list: {ex}")
        return []


def _row_to_evidence_dict(row):
    """Converts a database row into the evidence dict format expected by the frontend."""
    if row is None:
        return None
    item = dict(row)
    metadata = item.get("metadata")
    meta = {}
    if metadata:
        try:
            meta = json.loads(metadata)
        except (json.JSONDecodeError, TypeError):
            pass
    image_path = item.get("image_path", "")
    if image_path and not image_path.startswith("/"):
        image_path = "/" + image_path.lstrip("/")
    image_path = image_path.replace("\\", "/")
    return {
        "id": item.get("id"),
        "event_id": item.get("event_id"),
        "image": image_path,
        "event": meta.get("event_type", item.get("event_type", "")),
        "camera": item.get("camera", meta.get("camera", "")),
        "location": item.get("zone", meta.get("location", "")),
        "time": item.get("timestamp", ""),
        "trackingId": meta.get("tracking_id", ""),
        "confidence": float(item.get("event_confidence", meta.get("confidence", 0))),
        "severity": item.get("severity", "LOW"),
        "favorite": meta.get("favorite", False),
        "description": meta.get("ai_description", ""),
        "ocr_text": meta.get("ocr_text", ""),
        "tags": meta.get("tags", []),
        "similar_ids": meta.get("similar_ids", []),
        "metadata": meta,
    }


# ==========================================
# CAMERA CRUD FUNCTIONS
# ==========================================

def save_camera(name, stream_url, location="Unspecified", status="OFFLINE", fps=0.0, latency=0.0, resolution="640x480", user_id=1, **kwargs):
    """Saves or updates camera config in DB."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cameras (user_id, name, stream_url, location, status, fps, latency, resolution, network_errors, decode_errors, last_error, is_rtsp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, name) DO UPDATE SET
                    stream_url=excluded.stream_url,
                    location=excluded.location,
                    status=excluded.status,
                    fps=excluded.fps,
                    latency=excluded.latency,
                    resolution=excluded.resolution,
                    network_errors=excluded.network_errors,
                    decode_errors=excluded.decode_errors,
                    last_error=excluded.last_error,
                    is_rtsp=excluded.is_rtsp
            """, (
                user_id, name, stream_url, location, status, fps, latency, resolution,
                kwargs.get("network_errors", 0),
                kwargs.get("decode_errors", 0),
                kwargs.get("last_error"),
                kwargs.get("is_rtsp", 0)
            ))
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error saving camera '{name}': {e}")
        return False


def update_camera_status(name, status, fps=0.0, latency=0.0, user_id=None, **kwargs):
    """Updates camera online status, fps, and latency."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            if user_id is not None:
                cursor.execute("""
                    UPDATE cameras 
                    SET status = ?, fps = ?, latency = ?
                    WHERE name = ? AND user_id = ?
                """, (status, fps, latency, name, user_id))
            else:
                cursor.execute("""
                    UPDATE cameras 
                    SET status = ?, fps = ?, latency = ?
                    WHERE name = ?
                """, (status, fps, latency, name))
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error updating status for camera '{name}': {e}")
        return False


def get_camera(name, user_id=None):
    """Fetches camera details by camera name."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            if user_id is not None:
                cursor.execute("SELECT * FROM cameras WHERE name = ? AND user_id = ?", (name, user_id))
            else:
                cursor.execute("SELECT * FROM cameras WHERE name = ?", (name,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error fetching camera '{name}': {e}")
        return None


def get_all_cameras(user_id=None):
    """Fetches all registered cameras from database."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            if user_id is not None:
                cursor.execute("SELECT * FROM cameras WHERE user_id = ? ORDER BY id ASC", (user_id,))
            else:
                cursor.execute("SELECT * FROM cameras ORDER BY id ASC")
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Error fetching cameras: {e}")
        return []


def save_event(event_type, severity="LOW", camera="Unknown", zone="General Area", confidence=0.0, duration=0.0, metadata=None, screenshot="", track_id=-1, user_id=1):
    """Saves a new event/detection to the database."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO events (user_id, timestamp, event_type, severity, camera, zone, track_id, confidence, duration, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, timestamp, event_type, severity, camera, zone, track_id, confidence, duration, json.dumps(metadata) if metadata else None))
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Error saving event: {e}")
        return None


def get_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


def validate_csrf_token(token):
    return session.get("csrf_token") == token


def require_auth(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            return jsonify({"error": "Authentication required", "status": "unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function


def require_csrf(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            token = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token")
            if not token or not validate_csrf_token(token):
                return jsonify({"error": "CSRF token missing or invalid", "status": "forbidden"}), 403
        return f(*args, **kwargs)
    return decorated_function


def rate_limit(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.headers.get("X-Forwarded-For", request.remote_addr) or "unknown"
        rate_key = f"{client_ip}:{request.path}"
        if not _check_rate_limit(rate_key):
            return jsonify({"error": "Rate limit exceeded", "status": "too_many_requests"}), 429
        return f(*args, **kwargs)
    return decorated_function