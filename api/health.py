import time
import psutil
import sqlite3
import logging
from flask import Blueprint, jsonify, session
from database.db import DB_PATH, get_all_cameras
from api.auth import is_authenticated

health_bp = Blueprint("health_bp", __name__)
APP_START_TIME = time.time()
logger = logging.getLogger("SentinelX.Health")

def check_database():
    """Verifies SQLite connection and query execution latency."""
    try:
        start = time.time()
        conn = sqlite3.connect(DB_PATH, timeout=2)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        latency_ms = round((time.time() - start) * 1000, 2)
        return {"status": "HEALTHY", "latency_ms": latency_ms}
    except Exception as e:
        logger.error(f"Health Check Database Failure: {e}")
        return {"status": "UNHEALTHY", "error": str(e)}

@health_bp.route("/health", methods=["GET"])
@health_bp.route("/api/health", methods=["GET"])
def get_system_health():
    """Comprehensive System, Hardware, Database and Camera Stream Diagnostics.

    Public (unauthenticated) requests receive only minimal status — no
    hardware metrics, no database latency, no camera counts.  Authenticated
    dashboard users receive the full diagnostic payload.
    """
    uptime_seconds = int(time.time() - APP_START_TIME)
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    if not is_authenticated():
        return jsonify({
            "status": "HEALTHY",
            "timestamp": timestamp,
            "uptime_seconds": uptime_seconds
        }), 200

    # 1. CPU & Memory Stats
    cpu_percent = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    # 2. Camera Metrics Aggregation
    cameras = get_all_cameras()
    total_cams = len(cameras)
    online_cams = sum(1 for c in cameras if c.get("status") == "ONLINE")

    avg_fps = round(sum(c.get("fps", 0) for c in cameras) / total_cams, 1) if total_cams > 0 else 0.0
    avg_latency = round(sum(c.get("latency", 0) for c in cameras) / total_cams, 1) if total_cams > 0 else 0.0

    # 3. Overall System Uptime
    health_status = {
        "status": "HEALTHY",
        "timestamp": timestamp,
        "uptime_seconds": uptime_seconds,
        "hardware": {
            "cpu_usage_percent": cpu_percent,
            "ram": {
                "total_gb": round(ram.total / (1024**3), 2),
                "used_gb": round(ram.used / (1024**3), 2),
                "percent": ram.percent
            },
            "storage": {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent": disk.percent
            },
            "gpu": {
                "available": False,
                "name": "N/A",
                "usage_percent": 0
            }
        },
        "services": {
            "database": check_database(),
            "ai_engine": {"status": "RUNNING", "model": "YOLO11-Surveillance"},
            "cameras": {
                "total": total_cams,
                "online": online_cams,
                "avg_fps": avg_fps,
                "avg_latency_ms": avg_latency
            }
        }
    }

    return jsonify(health_status), 200