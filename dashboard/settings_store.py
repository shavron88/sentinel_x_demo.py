import json
import logging
from database.db import get_connection, get_all_cameras, save_camera

logger = logging.getLogger("SentinelX.Settings")

class SettingsStore:
    """Persists user and system settings in SQLite."""

    @staticmethod
    def _get_table():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                user_id INTEGER
            )
        """)
        conn.commit()
        return conn, cursor

    @staticmethod
    def get_setting(key, default=None, user_id=None):
        try:
            conn, cursor = SettingsStore._get_table()
            if user_id is not None:
                cursor.execute("SELECT value FROM settings WHERE key = ? AND user_id = ?", (key, user_id))
            else:
                cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            conn.close()
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
            conn, cursor = SettingsStore._get_table()
            if user_id is not None:
                cursor.execute(
                    "INSERT OR REPLACE INTO settings (key, value, user_id) VALUES (?, ?, ?)",
                    (key, json.dumps(value) if not isinstance(value, str) else value, user_id)
                )
            else:
                cursor.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                    (key, json.dumps(value) if not isinstance(value, str) else value)
                )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error setting {key}: {e}")
            return False

    @staticmethod
    def get_all_settings(user_id=None):
        try:
            conn, cursor = SettingsStore._get_table()
            if user_id is not None:
                cursor.execute("SELECT key, value FROM settings WHERE user_id = ?", (user_id,))
            else:
                cursor.execute("SELECT key, value FROM settings")
            rows = cursor.fetchall()
            conn.close()
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
