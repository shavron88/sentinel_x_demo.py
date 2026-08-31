import sqlite3
import json
import logging
from datetime import datetime

DB_PATH = "sentinelx.db"
logger = logging.getLogger("SentinelX.Database")


def get_connection():
    """Returns a thread-safe connection to SQLite with Row factory."""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates database schema tables if they do not exist."""
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

        # Migration: add columns if they don't exist (for existing DBs)
        try:
            cursor.execute("ALTER TABLE cameras ADD COLUMN network_errors INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE cameras ADD COLUMN decode_errors INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE cameras ADD COLUMN last_error TEXT")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE cameras ADD COLUMN is_rtsp INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE events ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE evidence ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE cameras ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE settings ADD COLUMN user_id INTEGER")
        except sqlite3.OperationalError:
            pass

        # Admin Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'System Administrator',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Seed default admin user if not exists
        import hashlib
        default_username = "sentinelx_admin"
        default_password = "SentinelX_SecurePassword2026!"
        default_password_hash = hashlib.sha256(default_password.encode()).hexdigest()
        cursor.execute(
            "INSERT OR IGNORE INTO admin_users (username, password_hash, email, role) VALUES (?, ?, ?, ?)",
            (default_username, default_password_hash, f"{default_username}@sentinelx.ai", "System Administrator")
        )

        conn.commit()
        logger.info("Database initialized successfully.")


init_db()

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
    """
    Updates camera online status, fps, and latency.
    **kwargs suppresses any unexpected keyword arguments (e.g. health, uptime, reconnects).
    """
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