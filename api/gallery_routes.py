from urllib.parse import quote

from flask import Blueprint, jsonify, request

from database.db import db_connection, get_all_evidence, get_all_cameras, get_event_stats
from camera.camera_manager import camera_manager
from api.auth import require_auth, get_current_user_id

gallery_bp = Blueprint('gallery_api', __name__, url_prefix='/api')


def _feed_url(name):
    """Browser-playable MJPEG URL for a camera.

    The DB column `stream_url` holds the capture *source* (a device index such as
    "0", or an rtsp:// URL), which is not something an <img> tag can render. The
    API previously echoed it straight back, so the UI tried to load "0" as a URL.
    """
    return "/video_feed?camera_name=%s" % quote(str(name), safe="")


@gallery_bp.route('/cameras', methods=['GET'])
@require_auth
def api_get_cameras():
    """Returns the current user's cameras merged with active camera streams."""
    try:
        user_id = get_current_user_id()
        # Only merge pipelines this user owns; the CameraManager singleton is
        # process-global, so get_all_status() otherwise exposes every tenant's
        # running cameras to whoever is logged in.
        try:
            active_cameras = camera_manager.get_status_for_user(user_id)
        except AttributeError:
            active_cameras = camera_manager.get_all_status()
        db_cameras = get_all_cameras(user_id=user_id)

        merged = {}

        # Add DB cameras first
        for cam in db_cameras:
            name = cam.get("name", "Unknown")
            merged[name] = {
                "id": cam.get("id", name),
                "name": name,
                "location": cam.get("location", "Unspecified"),
                "status": cam.get("status", "OFFLINE"),
                "source": cam.get("stream_url", ""),
                "stream": _feed_url(name),
                "fps": cam.get("fps", 0.0),
                "latency": cam.get("latency", 0.0),
                "resolution": cam.get("resolution", "640x480"),
                "health": "EXCELLENT" if cam.get("status") == "ONLINE" else "POOR",
                "is_recording": False,
                "zone": cam.get("location", "Unspecified")
            }

        # Merge/override with active camera stream data
        for name, cam in active_cameras.items():
            if name in merged:
                merged[name].update({
                    "status": cam.get("status", merged[name]["status"]),
                    "fps": cam.get("fps", merged[name]["fps"]),
                    "latency": cam.get("latency", merged[name]["latency"]),
                    "resolution": cam.get("resolution", merged[name]["resolution"]),
                    "health": cam.get("health", merged[name]["health"]),
                    "is_recording": cam.get("is_recording", merged[name]["is_recording"]),
                    "zone": cam.get("zone", merged[name]["zone"])
                })
            else:
                merged[name] = {
                    "id": name,
                    "name": name,
                    "location": cam.get("zone", "Unspecified"),
                    "status": cam.get("status", "OFFLINE"),
                    "source": "",
                    "stream": _feed_url(name),
                    "fps": cam.get("fps", 0.0),
                    "latency": cam.get("latency", 0.0),
                    "resolution": cam.get("resolution", "640x480"),
                    "health": cam.get("health", "POOR"),
                    "is_recording": cam.get("is_recording", False),
                    "zone": cam.get("zone", "Unspecified")
                }

        return jsonify(merged), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@gallery_bp.route('/gallery', methods=['GET'])
@require_auth
def api_get_gallery():
    """Fetches recorded evidence images and video logs for the current user."""
    try:
        user_id = get_current_user_id()
        limit = max(1, min(request.args.get("limit", 50, type=int) or 50, 500))
        with db_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM evidence WHERE user_id = ? ORDER BY id DESC LIMIT ?",
                (user_id, limit)
            ).fetchall()
            return jsonify([dict(row) for row in rows]), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@gallery_bp.route('/evidence', methods=['GET'])
@require_auth
def api_get_evidence():
    """Fetches evidence joined with event data for the evidence page."""
    try:
        limit = max(1, min(request.args.get("limit", 50, type=int) or 50, 500))
        data = get_all_evidence(limit=limit, user_id=get_current_user_id())
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@gallery_bp.route('/ai_summary', methods=['GET'])
@require_auth
def api_ai_summary():
    """Returns AI model detection summary metrics from the KPI rollup."""
    try:
        user_id = get_current_user_id()
        stats = get_event_stats(user_id=user_id)
        total = stats.get("total", 0)
        high_risk = stats.get("high_sev", 0)
        try:
            from ai.inference import YOLOInferenceEngine  # noqa: F401
            from config import MODEL_PATH
            import os
            model_status = "Active (YOLO11)" if os.path.exists(MODEL_PATH) else "Model weights missing"
        except Exception:
            model_status = "Unavailable"
        return jsonify({
            "total_detections_today": total,
            "high_risk_alerts": high_risk,
            "model_status": model_status,
            "accuracy": round(float(stats.get("avg_confidence", 0.0)) * 100, 1),
            "persons": stats.get("person_events", 0),
            "vehicles": stats.get("vehicle_events", 0),
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
