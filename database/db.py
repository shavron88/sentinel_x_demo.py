import sqlite3
import json
import logging

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
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT DEFAULT 'LOW',
                camera TEXT NOT NULL,
                zone TEXT DEFAULT 'General Area',
                confidence REAL DEFAULT 0.0,
                duration REAL DEFAULT 0.0,
                metadata TEXT
            )
        """)

        # Evidence Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                name TEXT UNIQUE NOT NULL,
                location TEXT DEFAULT 'Unspecified',
                stream_url TEXT NOT NULL,
                status TEXT DEFAULT 'OFFLINE',
                fps REAL DEFAULT 0.0,
                latency REAL DEFAULT 0.0,
                resolution TEXT DEFAULT '640x480'
            )
        """)

        conn.commit()
        logger.info("Database initialized successfully.")


# ==========================================
# EVENTS & EVIDENCE FUNCTIONS
# ==========================================

def get_all_events(limit=50):
    """Fetches recent recorded events from database."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        return []


def get_evidence_by_id(evidence_id):
    """Fetches single evidence record."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM evidence WHERE id = ?", (evidence_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error fetching evidence: {e}")
        return None


# ==========================================
# CAMERA CRUD FUNCTIONS
# ==========================================

def save_camera(name, stream_url, location="Unspecified", status="OFFLINE", fps=0.0, latency=0.0, resolution="640x480", **kwargs):
    """Saves or updates camera config in DB."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cameras (name, stream_url, location, status, fps, latency, resolution)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    stream_url=excluded.stream_url,
                    location=excluded.location,
                    status=excluded.status,
                    fps=excluded.fps,
                    latency=excluded.latency,
                    resolution=excluded.resolution
            """, (name, stream_url, location, status, fps, latency, resolution))
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error saving camera '{name}': {e}")
        return False


def update_camera_status(name, status, fps=0.0, latency=0.0, **kwargs):
    """
    Updates camera online status, fps, and latency.
    **kwargs suppresses any unexpected keyword arguments (e.g. health, uptime, reconnects).
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
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


def get_camera(name):
    """Fetches camera details by camera name."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cameras WHERE name = ?", (name,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error fetching camera '{name}': {e}")
        return None


def get_all_cameras():
    """Fetches all registered cameras from database."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cameras ORDER BY id ASC")
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Error fetching cameras: {e}")
        return []