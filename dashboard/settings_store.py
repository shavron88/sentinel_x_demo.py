import json
import logging
from database.db import db_connection, db_write_connection, save_camera

logger = logging.getLogger("SentinelX.Settings")

class SettingsStore:
    """Persists user and system settings in SQLite.

    The ``settings`` table is created and migrated by ``database.db.init_db`` and
    uses PRIMARY KEY (key, user_id) so each user has an independent namespace.
    """

    @staticmethod
    def get_setting(key, default=None, user_id=None):
        try:
            with db_connection() as conn:
                if user_id is not None:
                    row = conn.execute(
                        "SELECT value FROM settings WHERE key = ? AND user_id = ?", (key, user_id)
                    ).fetchone()
                else:
                    row = conn.execute(
                        "SELECT value FROM settings WHERE key = ? ORDER BY user_id LIMIT 1", (key,)
                    ).fetchone()
                if row:
                    try:
                        return json.loads(row['value'])
                    except (json.JSONDecodeError, TypeError):
                        return row['value']
                return default
        except Exception as e:
            logger.error(f"Error getting setting {key}: {e}")
            return default

    @staticmethod
    def set_setting(key, value, user_id=None):
        try:
            stored = value if isinstance(value, str) else json.dumps(value)
            effective_user = 1 if user_id is None else user_id
            with db_write_connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO settings (key, value, user_id) VALUES (?, ?, ?)",
                    (key, stored, effective_user)
                )
            return True
        except Exception as e:
            logger.error(f"Error setting {key}: {e}")
            return False

    @staticmethod
    def get_all_settings(user_id=None):
        try:
            with db_connection() as conn:
                if user_id is not None:
                    rows = conn.execute(
                        "SELECT key, value FROM settings WHERE user_id = ?", (user_id,)
                    ).fetchall()
                else:
                    rows = conn.execute("SELECT key, value FROM settings").fetchall()
                settings = {}
                for row in rows:
                    try:
                        settings[row['key']] = json.loads(row['value'])
                    except (json.JSONDecodeError, TypeError):
                        settings[row['key']] = row['value']
                return settings
        except Exception as e:
            logger.error(f"Error getting all settings: {e}")
            return {}

    @staticmethod
    def save_camera_settings(cameras, user_id=1):
        results = []
        for cam in cameras:
            try:
                success = save_camera(
                    name=cam.get('name', ''),
                    stream_url=cam.get('stream_url', ''),
                    location=cam.get('location', ''),
                    status='ONLINE' if cam.get('enabled') else 'OFFLINE',
                    fps=float(cam.get('fps', 30)),
                    latency=cam.get('latency', 0),
                    resolution=cam.get('resolution', '640x480'),
                    user_id=user_id
                )
                results.append({'name': cam.get('name'), 'success': success})
            except Exception as e:
                logger.error(f"Error saving camera {cam.get('name')}: {e}")
                results.append({'name': cam.get('name'), 'success': False, 'error': str(e)})
        return results
