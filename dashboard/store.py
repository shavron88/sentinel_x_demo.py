import logging

try:
    from database.db import (
        get_all_events,
        get_all_cameras,
        get_event_stats,
        PERSON_EVENT_TYPES,
        VEHICLE_EVENT_TYPES,
    )
except ImportError:  # pragma: no cover - defensive
    def get_all_events(limit=50, user_id=None, **kwargs):
        return []
    def get_all_cameras(user_id=None):
        return []
    def get_event_stats(user_id=None, **kwargs):
        return {}
    PERSON_EVENT_TYPES = ()
    VEHICLE_EVENT_TYPES = ()

logger = logging.getLogger("SentinelX.Store")

# In-memory stores for real-time updates
_memory_events = []
_memory_stats = {
    "total_cameras": 0,
    "online_cameras": 0,
    "total_incidents": 0,
    "high_severity_incidents": 0,
    "threat_level": "LOW",
    "fps": 0.0,
    "persons": 0,
    "vehicles": 0,
    "alerts": 0,
    "threat": "LOW"
}


def add_event(event):
    """Adds an event to the in-memory events list."""
    global _memory_events
    _memory_events.insert(0, event)
    _memory_events = _memory_events[:100]


def update_stats(persons=0, vehicles=0, threat="LOW", fps=0.0):
    """Updates the in-memory stats with latest values."""
    global _memory_stats
    _memory_stats["persons"] = persons
    _memory_stats["vehicles"] = vehicles
    _memory_stats["threat"] = threat
    _memory_stats["fps"] = fps


def get_events(limit=20, user_id=None):
    """Returns events from DB, falling back to in-memory if DB is empty."""
    db_events = get_all_events(limit=limit, user_id=user_id)
    if db_events:
        return db_events
    return _memory_events[:limit]


def get_stats(user_id=None):
    """Returns stats from DB, falling back to in-memory if DB is empty."""
    try:
        db_stats = _compute_db_stats(user_id=user_id)
        if db_stats.get("total_incidents", 0) > 0 or db_stats.get("total_cameras", 0) > 0:
            return db_stats
        return dict(_memory_stats)
    except Exception as e:
        logger.error(f"Error calculating stats: {e}")
        return dict(_memory_stats)


def _compute_db_stats(user_id=None):
    """Builds the dashboard KPI payload.

    Incident/person/vehicle counters come from the ``event_stats_daily``
    rollup (all-time) instead of scanning the last 100 event rows, which both
    capped the counters at 100 and cost a full scan per poll.
    """
    cameras = get_all_cameras(user_id=user_id)
    totals = get_event_stats(user_id=user_id)

    total_cameras = len(cameras)
    online_cameras = sum(1 for c in cameras if (c.get("status") or "").upper() == "ONLINE")

    total_events = int(totals.get("total", 0) or 0)
    high_severity_count = int(totals.get("high_sev", 0) or 0)

    threat_level = "LOW"
    if high_severity_count > 5:
        threat_level = "CRITICAL"
    elif high_severity_count > 0:
        threat_level = "MEDIUM"

    avg_fps = 0.0
    if total_cameras > 0:
        fps_sum = sum(float(c.get("fps") or 0.0) for c in cameras)
        avg_fps = round(fps_sum / total_cameras, 1)

    return {
        "total_cameras": total_cameras,
        "online_cameras": online_cameras,
        "total_incidents": total_events,
        "high_severity_incidents": high_severity_count,
        "threat_level": threat_level,
        "fps": avg_fps,
        "persons": int(totals.get("person_events", 0) or 0),
        "vehicles": int(totals.get("vehicle_events", 0) or 0),
        "alerts": high_severity_count,
        "threat": threat_level,
    }
