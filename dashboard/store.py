import logging

try:
    from database.db import get_all_events, get_all_cameras
except ImportError:
    # Safe Fallback agar db functions import mein problem ho
    def get_all_events(limit=50):
        return []
    def get_all_cameras():
        return []

logger = logging.getLogger("SentinelX.Store")

def get_events(limit=20):
    return get_all_events(limit=limit)

def get_stats():
    try:
        events = get_all_events(limit=100)
        cameras = get_all_cameras()

        total_cameras = len(cameras)
        online_cameras = sum(1 for c in cameras if c.get("status") == "ONLINE")
        total_events = len(events)
        high_severity_count = sum(1 for e in events if e.get("severity") == "HIGH")

        threat_level = "NOMINAL"
        if high_severity_count > 5:
            threat_level = "CRITICAL"
        elif high_severity_count > 0:
            threat_level = "ELEVATED"

        return {
            "total_cameras": total_cameras,
            "online_cameras": online_cameras,
            "total_incidents": total_events,
            "high_severity_incidents": high_severity_count,
            "threat_level": threat_level
        }
    except Exception as e:
        logger.error(f"Error calculating stats: {e}")
        return {
            "total_cameras": 0,
            "online_cameras": 0,
            "total_incidents": 0,
            "high_severity_incidents": 0,
            "threat_level": "UNKNOWN"
        }