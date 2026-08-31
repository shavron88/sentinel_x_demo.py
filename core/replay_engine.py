import os
import cv2
import json
import logging
from datetime import datetime, timedelta
from database.db import get_connection, get_evidence_by_id

logger = logging.getLogger("SentinelX.ReplayEngine")

class ReplayEngine:
    """Engine to fetch, construct, and stream incident replays."""

    @staticmethod
    def get_replay_by_event(event_id):
        """Fetches incident evidence images or video clips associated with an event ID."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.*, ev.image_path, ev.metadata 
                FROM events e 
                LEFT JOIN evidence ev ON e.id = ev.event_id 
                WHERE e.id = ?
            """, (event_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    @staticmethod
    def get_replays_by_time_range(camera_name, start_time_str, end_time_str):
        """Returns evidence clips/snapshots recorded for a camera between specific times."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM evidence 
                WHERE camera = ? AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            """, (camera_name, start_time_str, end_time_str))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_recent_replay_clip(camera_name, minutes=5):
        """Fetches all evidence snapshots captured in the last X minutes for quick playback."""
        cutoff = (datetime.now() - timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM evidence 
                WHERE camera = ? AND timestamp >= ?
                ORDER BY timestamp ASC
            """, (camera_name, cutoff))
            return [dict(row) for row in cursor.fetchall()]