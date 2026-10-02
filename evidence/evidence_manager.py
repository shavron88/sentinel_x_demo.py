import cv2
import os
import json
import logging
import sqlite3
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Absolute, CWD-independent paths. A relative DB path silently created a second
# database whenever the process was launched from another directory.
try:
    from config import DB_PATH
except Exception:  # pragma: no cover
    DB_PATH = os.getenv("DB_PATH", "sentinelx.db")
    if not os.path.isabs(DB_PATH):
        DB_PATH = os.path.join(PROJECT_ROOT, DB_PATH)
EVIDENCE_DIR = os.path.join(PROJECT_ROOT, "evidence", "screenshots")
logger = logging.getLogger("SentinelX.EvidenceManager")

try:
    from database.db import init_db
    init_db()
except Exception:
    pass


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


class EvidenceManager:
    def save(self, frame, event_type, track_id=-1, event_id=None, camera="Unknown", user_id=1):
        return save(frame, event_type, track_id, event_id, camera, user_id)


def save(frame, event_type, track_id=-1, event_id=None, camera="Unknown", user_id=1):
    """Saves annotated frame as evidence image and records it in the database."""
    conn = None
    try:
        os.makedirs(EVIDENCE_DIR, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"evidence_{timestamp}_track{track_id}.jpg"
        filepath = os.path.join(EVIDENCE_DIR, filename)

        if not cv2.imwrite(filepath, frame):
            raise IOError(f"Failed to write evidence image: {filepath}")

        # Store a project-relative, forward-slashed path for cross-platform reads
        db_filepath = os.path.relpath(filepath, PROJECT_ROOT).replace("\\", "/")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO evidence (user_id, event_id, camera, image_path, metadata, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            event_id,
            camera,
            db_filepath,
            json.dumps({
                "event_type": event_type,
                "tracking_id": track_id,
                "saved_at": datetime.now().isoformat()
            }),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        logger.error(f"Error saving evidence: {e}")
        return None
    finally:
        if conn is not None:
            conn.close()
