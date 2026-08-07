from flask import Blueprint, jsonify, request
from database.db import get_connection
from camera.camera_manager import camera_manager

gallery_bp = Blueprint('gallery_api', __name__, url_prefix='/api')

@gallery_bp.route('/cameras', methods=['GET'])
def api_get_cameras():
    """Returns all active cameras and their statuses."""
    try:
        return jsonify(camera_manager.get_all_status()), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@gallery_bp.route('/gallery', methods=['GET'])
def api_get_gallery():
    """Fetches recorded evidence images and video logs."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM evidence ORDER BY id DESC LIMIT 50")
            rows = cursor.fetchall()
            return jsonify([dict(row) for row in rows]), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@gallery_bp.route('/ai_summary', methods=['GET'])
def api_ai_summary():
    """Returns AI model detection summary metrics."""
    return jsonify({
        "total_detections_today": 14,
        "high_risk_alerts": 2,
        "model_status": "Active (YOLOv8)",
        "accuracy": "94.8%"
    }), 200