import os
import cv2
import json
import logging
from datetime import datetime, timedelta

from database.db import db_connection, get_evidence_by_id

logger = logging.getLogger("SentinelX.ReplayEngine")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ReplayEngine:
    """Engine to fetch, construct, and stream incident replays.

    Every query is scoped by ``user_id``; these helpers are reachable from
    authenticated routes and previously returned any tenant's footage.
    """

    @staticmethod
    def _web_path(image_path):
        """Turns a stored filesystem path into a browser-usable URL."""
        if not image_path:
            return None
        path = str(image_path).replace("\\", "/")
        if path.startswith("evidence/"):
            return "/" + path
        return "/evidence/screenshots/" + os.path.basename(path)

    @staticmethod
    def get_replay_by_event(event_id, user_id=None):
        """Fetches incident evidence images or video clips associated with an event ID."""
        with db_connection() as conn:
            if user_id is not None:
                cursor = conn.execute("""
                    SELECT ev.id AS evidence_id, ev.event_id, ev.camera, ev.image_path,
                           ev.timestamp AS captured_at, ev.metadata AS evidence_metadata,
                           e.event_type, e.severity, e.zone, e.confidence,
                           e.duration, e.track_id
                    FROM events e
                    LEFT JOIN evidence ev ON ev.event_id = e.id
                    WHERE e.id = ? AND e.user_id = ?
                """, (event_id, user_id))
            else:
                cursor = conn.execute("""
                    SELECT ev.id AS evidence_id, ev.event_id, ev.camera, ev.image_path,
                           ev.timestamp AS captured_at, ev.metadata AS evidence_metadata,
                           e.event_type, e.severity, e.zone, e.confidence,
                           e.duration, e.track_id
                    FROM events e
                    LEFT JOIN evidence ev ON ev.event_id = e.id
                    WHERE e.id = ?
                """, (event_id,))
            row = cursor.fetchone()
            if not row:
                return None

            result = dict(row)
            # `SELECT e.*, ev.metadata` produced two columns named `metadata`;
            # sqlite3 keyed the dict by name so one silently overwrote the other.
            # They are now explicitly aliased and merged here.
            raw_metadata = result.get("evidence_metadata")
            result.pop("evidence_metadata", None)
            meta = {}
            if raw_metadata:
                try:
                    meta = json.loads(raw_metadata)
                except (json.JSONDecodeError, TypeError):
                    meta = {}
            result["metadata"] = meta
            result["url"] = ReplayEngine._web_path(result.get("image_path"))
            return result

    @staticmethod
    def get_replays_by_time_range(camera_name, start_time_str, end_time_str, user_id=None):
        """Returns evidence clips/snapshots recorded for a camera between specific times."""
        params = [camera_name, start_time_str, end_time_str]
        user_clause = ""
        if user_id is not None:
            user_clause = " AND user_id = ?"
            params.append(user_id)
        with db_connection() as conn:
            rows = conn.execute(f"""
                SELECT * FROM evidence
                WHERE camera = ? AND timestamp BETWEEN ? AND ?{user_clause}
                ORDER BY timestamp ASC
            """, params).fetchall()
        return [ReplayEngine._decorate(dict(r)) for r in rows]

    @staticmethod
    def get_recent_replay_clip(camera_name, minutes=5, user_id=None):
        """Fetches all evidence snapshots captured in the last X minutes for quick playback."""
        cutoff = (datetime.now() - timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")
        params = [camera_name, cutoff]
        user_clause = ""
        if user_id is not None:
            user_clause = " AND user_id = ?"
            params.append(user_id)
        with db_connection() as conn:
            rows = conn.execute(f"""
                SELECT * FROM evidence
                WHERE camera = ? AND timestamp >= ?{user_clause}
                ORDER BY timestamp ASC
            """, params).fetchall()
        return [ReplayEngine._decorate(dict(r)) for r in rows]

    @staticmethod
    def _decorate(record):
        record["url"] = ReplayEngine._web_path(record.get("image_path"))
        raw_metadata = record.get("metadata")
        if isinstance(raw_metadata, str):
            try:
                record["metadata"] = json.loads(raw_metadata)
            except (json.JSONDecodeError, TypeError):
                record["metadata"] = {}
        return record
