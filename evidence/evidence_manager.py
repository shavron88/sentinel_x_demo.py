import cv2
import os
import json
import logging
import sqlite3
from datetime import datetime

DB_PATH = "sentinelx.db"
EVIDENCE_DIR = "evidence/screenshots"
logger = logging.getLogger("SentinelX.EvidenceManager")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class EvidenceManager:
    def save(self, frame, event_type, track_id=-1, event_id=None, camera="Unknown"):
        return save(frame, event_type, track_id, event_id, camera)


def save(frame, event_type, track_id=-1, event_id=None, camera="Unknown"):
    """Saves annotated frame as evidence image and records it in the database."""
    try:
        os.makedirs(EVIDENCE_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"evidence_{timestamp}_track{track_id}.jpg"
        filepath = os.path.join(EVIDENCE_DIR, filename)
        
        cv2.imwrite(filepath, frame)
        
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO evidence (event_id, camera, image_path, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                event_id,
                camera,
                filepath,
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
