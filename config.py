# ==========================================
# SentinelX Configuration
# ==========================================

import os
import sys
from typing import Optional


def _load_dotenv(path=".env"):
    """Minimal .env loader — no external dependency required."""
    if not os.path.isfile(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


_load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))


# Project root directory (where this config.py lives)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def _get_env(key: str, default=None):
    """Get environment variable with optional default."""
    return os.getenv(key, default)


def _resolve_path(relative_path: str) -> str:
    """Resolve a relative path against the project root to ensure correct loading."""
    if os.path.isabs(relative_path):
        return relative_path
    return os.path.join(PROJECT_ROOT, relative_path)


# ==========================================
# Application
# ==========================================
DEBUG = _get_env("FLASK_DEBUG", "0") == "1"
HOST = _get_env("FLASK_HOST", "0.0.0.0")
PORT = int(_get_env("FLASK_PORT", "5000"))
SECRET_KEY = _get_env("SECRET_KEY", "sentinelx-dev-key-change-in-production")

# ==========================================
# AI Model  (YOLO11 via the Ultralytics ecosystem)
# ==========================================
# YOLO11n is the smallest real-time model; ideal for CPU edge inference.
# Swap to yolo11s.pt / yolo11m.pt for higher accuracy on capable hardware.
_raw_model_path = _get_env("MODEL_PATH", "models/yolo11n.pt")
MODEL_PATH = _resolve_path(_raw_model_path)
CONFIDENCE_THRESHOLD = float(_get_env("CONFIDENCE_THRESHOLD", "0.50"))
# IoU threshold for Non-Maximum Suppression (lower = more aggressive suppression of duplicates)
IOU_THRESHOLD = float(_get_env("IOU_THRESHOLD", "0.45"))
# Inference resolution (YOLO letterbox-resizes to this; smaller = faster on CPU)
IMAGE_SIZE = int(_get_env("IMAGE_SIZE", "320"))
# Inference device: "auto" = CUDA if available else CPU, or explicit "cuda"/"cpu"
DEVICE = _get_env("DEVICE", "auto")
# Comma-separated list of COCO class IDs to retain for surveillance.
# person(0), bicycle(1), car(2), motorcycle(3), bus(5), truck(7),
# backpack(24), handbag(26), suitcase(28)  (last three feed the abandoned-object detector)
_raw_target_classes = _get_env("TARGET_CLASSES", "0,1,2,3,5,7,24,26,28")
TARGET_CLASSES = [int(c) for c in _raw_target_classes.split(",") if c.strip().lstrip("-").isdigit()]
# Enable/disable multi-object tracking (ByteTrack). When disabled, detection-only mode is used.
TRACKING_ENABLED = _get_env("TRACKING_ENABLED", "1") == "1"
# ByteTrack config filename shipped with Ultralytics.
TRACKER = _get_env("TRACKER", "bytetrack.yaml")

# ==========================================
# Camera Configuration
# ==========================================
CAMERA_SOURCE = _get_env("CAMERA_SOURCE", "1")

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
# Recorded CCTV Video File (Second Camera)
# ==========================================
# Set VIDEO_FILE env var to a video file path to auto-register as Recorded_CCTV
VIDEO_FILE = _get_env("VIDEO_FILE", "")
VIDEO_FILE_NAME = _get_env("VIDEO_FILE_NAME", "Recorded_CCTV")
VIDEO_FILE_ZONE = _get_env("VIDEO_FILE_ZONE", "Demo Zone")

if VIDEO_FILE and os.path.isfile(VIDEO_FILE):
    CAMERAS.append({
        "name": VIDEO_FILE_NAME,
        "source": VIDEO_FILE,
        "zone": VIDEO_FILE_ZONE,
    })

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
EVIDENCE_DIR = _resolve_path(_get_env("EVIDENCE_DIR", "evidence/screenshots"))
VIDEO_DIR = _resolve_path(_get_env("VIDEO_DIR", "evidence/videos"))
MODELS_DIR = _resolve_path(_get_env("MODELS_DIR", "models"))
DB_PATH = _resolve_path(_get_env("DB_PATH", "sentinelx.db"))
LOG_DIR = _resolve_path(_get_env("LOG_DIR", "logs"))

# ==========================================
# Performance
# ==========================================
MAX_QUEUE_SIZE = int(_get_env("MAX_QUEUE_SIZE", "10"))
FRAME_SKIP = int(_get_env("FRAME_SKIP", "2"))
INFERENCE_INTERVAL = float(_get_env("INFERENCE_INTERVAL", "0.02"))
VIDEO_FRAME_SKIP = int(_get_env("VIDEO_FRAME_SKIP", "3"))

# ==========================================
# Dashboard
# ==========================================
DASHBOARD_REFRESH_INTERVAL = int(_get_env("DASHBOARD_REFRESH_INTERVAL", "2000"))
STREAM_QUALITY = int(_get_env("STREAM_QUALITY", "70"))

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
