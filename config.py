# ==========================================
# SentinelX Configuration
# ==========================================

import os
from typing import Optional


def _get_env(key: str, default=None):
    """Get environment variable with optional default."""
    return os.getenv(key, default)


# ==========================================
# Application
# ==========================================
DEBUG = _get_env("FLASK_DEBUG", "0") == "1"
HOST = _get_env("FLASK_HOST", "0.0.0.0")
PORT = int(_get_env("FLASK_PORT", "5000"))
SECRET_KEY = _get_env("SECRET_KEY", "sentinelx-dev-key-change-in-production")

# ==========================================
# AI Model
# ==========================================
MODEL_PATH = _get_env("MODEL_PATH", "models/yolov8m.pt")
CONFIDENCE_THRESHOLD = float(_get_env("CONFIDENCE_THRESHOLD", "0.60"))

# ==========================================
# Camera Configuration
# ==========================================
CAMERA_SOURCE = _get_env("CAMERA_SOURCE", "0")

# Multi-camera configuration from environment
# Format: name:source:zone[:timeout]
# Separate cameras with | to avoid conflicts with RTSP URLs containing :
CAMERAS = []
_cameras_env = _get_env("CAMERAS", "")
if _cameras_env:
    for cam_str in _cameras_env.split("|"):
        parts = cam_str.strip().split(":")
        if len(parts) >= 3:
            name = parts[0]
            # Check if last part is a timeout (all digits)
            if len(parts) > 3 and parts[-1].isdigit():
                timeout = int(parts[-1])
                zone = parts[-2]
                source = ":".join(parts[1:-2])
            else:
                timeout = None
                zone = parts[-1]
                source = ":".join(parts[1:-1])
            
            cam = {
                "name": name,
                "source": source,
                "zone": zone,
            }
            if timeout is not None:
                cam["timeout"] = timeout
            CAMERAS.append(cam)

# ==========================================
# RTSP Settings
# ==========================================
RTSP_TIMEOUT_MS = int(_get_env("RTSP_TIMEOUT_MS", "5000"))
RTSP_BUFFER_SIZE = int(_get_env("RTSP_BUFFER_SIZE", "1"))
RTSP_TRANSPORT = _get_env("RTSP_TRANSPORT", "tcp")
RTSP_MAX_RECONNECT_DELAY = float(_get_env("RTSP_MAX_RECONNECT_DELAY", "30.0"))
RTSP_RECONNECT_BACKOFF = float(_get_env("RTSP_RECONNECT_BACKOFF", "1.5"))

DEFAULT_RTSP_CONFIG = {
    "timeout_ms": RTSP_TIMEOUT_MS,
    "buffer_size": RTSP_BUFFER_SIZE,
    "transport": RTSP_TRANSPORT,
    "max_reconnect_delay": RTSP_MAX_RECONNECT_DELAY,
    "reconnect_backoff_factor": RTSP_RECONNECT_BACKOFF,
}

# ==========================================
# Event Settings
# ==========================================
EVENT_COOLDOWN = int(_get_env("EVENT_COOLDOWN", "600"))
LOITERING_THRESHOLD = int(_get_env("LOITERING_THRESHOLD", "30"))
CROWD_THRESHOLD = int(_get_env("CROWD_THRESHOLD", "5"))

# ==========================================
# Paths
# ==========================================
EVIDENCE_DIR = _get_env("EVIDENCE_DIR", "evidence/screenshots")
VIDEO_DIR = _get_env("VIDEO_DIR", "evidence/videos")
MODELS_DIR = _get_env("MODELS_DIR", "models")
DB_PATH = _get_env("DB_PATH", "sentinelx.db")
LOG_DIR = _get_env("LOG_DIR", "logs")

# ==========================================
# Performance
# ==========================================
MAX_QUEUE_SIZE = int(_get_env("MAX_QUEUE_SIZE", "30"))
FRAME_SKIP = int(_get_env("FRAME_SKIP", "1"))
INFERENCE_INTERVAL = float(_get_env("INFERENCE_INTERVAL", "0.01"))

# ==========================================
# Dashboard
# ==========================================
DASHBOARD_REFRESH_INTERVAL = int(_get_env("DASHBOARD_REFRESH_INTERVAL", "1000"))
STREAM_QUALITY = int(_get_env("STREAM_QUALITY", "80"))

# ==========================================
# Demo Mode
# ==========================================
DEMO_MODE = _get_env("SENTINELX_DEMO", "0") == "1"

# ==========================================
# Database
# ==========================================
DATABASE_URL = _get_env("DATABASE_URL", f"sqlite:///{DB_PATH}")

# ==========================================
# Logging
# ==========================================
LOG_LEVEL = _get_env("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_FILE = os.path.join(LOG_DIR, "sentinelx.log")

# Ensure directories exist
os.makedirs(EVIDENCE_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
