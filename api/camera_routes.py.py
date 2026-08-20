import logging
from flask import Blueprint, jsonify, request
from database.db import get_all_cameras, get_camera, save_camera
from api.auth import require_auth, require_csrf

camera_bp = Blueprint("camera_bp", __name__)
logger = logging.getLogger("SentinelX.CameraAPI")

@camera_bp.route("/api/cameras", methods=["GET"])
def list_cameras():
    cameras = get_all_cameras()
    return jsonify({"success": True, "count": len(cameras), "cameras": cameras})

@camera_bp.route("/api/cameras/<string:name>", methods=["GET"])
def get_single_camera(name):
    camera = get_camera(name)
    if camera:
        return jsonify({"success": True, "camera": camera})
    return jsonify({"success": False, "error": "Camera not found"}), 404

@camera_bp.route("/api/cameras", methods=["POST"])
@require_auth
@require_csrf
def add_or_update_camera():
    data = request.json or {}
    name = data.get("name")
    stream_url = data.get("stream_url")

    if not name or not stream_url:
        return jsonify({"success": False, "error": "Name and stream_url required"}), 400

    location = data.get("location", "Unspecified")
    success = save_camera(name=name, stream_url=stream_url, location=location)

    if success:
        return jsonify({"success": True, "message": f"Camera '{name}' saved successfully"})
    return jsonify({"success": False, "error": "Failed to save camera"}), 500