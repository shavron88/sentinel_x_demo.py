from flask import Blueprint, jsonify, request

from core.replay_engine import ReplayEngine
from api.auth import require_auth, get_current_user_id

replay_bp = Blueprint("replay_bp", __name__)

# Bounds on the replay window so a single request cannot scan the whole table.
MAX_REPLAY_MINUTES = 60
MAX_REPLAY_RESULTS = 500


def _bounded_minutes(raw, default=5):
    try:
        minutes = int(raw)
    except (TypeError, ValueError):
        return default
    return max(1, min(minutes, MAX_REPLAY_MINUTES))


# 1. GET /api/replay/event/<event_id>
@replay_bp.route("/api/replay/event/<int:event_id>", methods=["GET"])
@require_auth
def api_replay_event(event_id):
    # Scoped by user: without this any authenticated user could replay any
    # event id and pull another tenant's footage.
    replay_data = ReplayEngine.get_replay_by_event(event_id, user_id=get_current_user_id())
    if replay_data:
        return jsonify({"success": True, "replay": replay_data})
    return jsonify({"success": False, "error": f"No replay found for Event ID {event_id}"}), 404


# 2. GET /api/replay/recent?camera=Camera-1&minutes=5
@replay_bp.route("/api/replay/recent", methods=["GET"])
@require_auth
def api_replay_recent():
    camera = request.args.get("camera", "Camera-01")
    minutes = _bounded_minutes(request.args.get("minutes"))

    replays = ReplayEngine.get_recent_replay_clip(
        camera, minutes, user_id=get_current_user_id()
    )
    return jsonify({
        "success": True,
        "camera": camera,
        "timeframe_minutes": minutes,
        "frames_count": len(replays),
        "replays": replays[:MAX_REPLAY_RESULTS]
    })


# 3. GET /api/replay/range?camera=Camera-1&start=...&end=...
@replay_bp.route("/api/replay/range", methods=["GET"])
@require_auth
def api_replay_range():
    camera = request.args.get("camera")
    start = request.args.get("start")
    end = request.args.get("end")

    if not camera or not start or not end:
        return jsonify({
            "success": False,
            "error": "Parameters 'camera', 'start', and 'end' are required"
        }), 400

    if end < start:
        return jsonify({"success": False, "error": "'end' must not precede 'start'"}), 400

    replays = ReplayEngine.get_replays_by_time_range(
        camera, start, end, user_id=get_current_user_id()
    )
    return jsonify({"success": True, "replays": replays[:MAX_REPLAY_RESULTS]})
