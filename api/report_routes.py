from flask import Blueprint, jsonify, request, send_file
import os
from core.replay_engine import ReplayEngine

replay_bp = Blueprint("replay_bp", __name__)

# 1. GET /api/replay/event/<event_id>
@replay_bp.route("/api/replay/event/<int:event_id>", methods=["GET"])
def api_replay_event(event_id):
    replay_data = ReplayEngine.get_replay_by_event(event_id)
    if replay_data:
        return jsonify({"success": True, "replay": replay_data})
    return jsonify({"success": False, "error": f"No replay found for Event ID {event_id}"}), 404


# 2. GET /api/replay/recent?camera=Camera-1&minutes=5
@replay_bp.route("/api/replay/recent", methods=["GET"])
def api_replay_recent():
    camera = request.args.get("camera", "Camera-1")
    minutes = int(request.args.get("minutes", 5))

    replays = ReplayEngine.get_recent_replay_clip(camera, minutes)
    return jsonify({
        "success": True,
        "camera": camera,
        "timeframe_minutes": minutes,
        "frames_count": len(replays),
        "replays": replays
    })


# 3. GET /api/replay/range?camera=Camera-1&start=...&end=...
@replay_bp.route("/api/replay/range", methods=["GET"])
def api_replay_range():
    camera = request.args.get("camera")
    start = request.args.get("start")
    end = request.args.get("end")

    if not camera or not start or not end:
        return jsonify({"success": False, "error": "Parameters 'camera', 'start', and 'end' are required"}), 400

    replays = ReplayEngine.get_replays_by_time_range(camera, start, end)
    return jsonify({"success": True, "replays": replays})