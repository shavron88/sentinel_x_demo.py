import sys
from flask import Blueprint, jsonify, request, session
from camera.camera_manager import camera_manager

camera_bp = Blueprint('camera', __name__, url_prefix='/api/camera')


def _get_current_user_id():
    """Get current user ID from session, defaulting to 1."""
    return session.get("user_id", 1)


@camera_bp.route('/snapshot', methods=['POST'])
def handle_snapshot():
    data = request.get_json() or {}
    cam_name = data.get('camera_name', 'Camera_01')
    
    stream = camera_manager.get_camera_stream(cam_name)
    if not stream:
        return jsonify({"success": False, "error": f"Camera '{cam_name}' not found"}), 404
        
    success, result = stream.take_snapshot()
    if success:
        return jsonify({"success": True, "image": result}), 200
    return jsonify({"success": False, "error": result}), 500


@camera_bp.route('/start-record', methods=['POST'])
def handle_start_record():
    data = request.get_json() or {}
    cam_name = data.get('camera_name', 'Camera_01')
    
    stream = camera_manager.get_camera_stream(cam_name)
    if not stream:
        return jsonify({"success": False, "error": f"Camera '{cam_name}' not found"}), 404
        
    success, result = stream.start_recording()
    if success:
        return jsonify({"success": True, "file": result, "message": "Recording started"}), 200
    return jsonify({"success": False, "error": result}), 400


@camera_bp.route('/stop-record', methods=['POST'])
def handle_stop_record():
    data = request.get_json() or {}
    cam_name = data.get('camera_name', 'Camera_01')
    
    stream = camera_manager.get_camera_stream(cam_name)
    if not stream:
        return jsonify({"success": False, "error": f"Camera '{cam_name}' not found"}), 404
        
    success, result = stream.stop_recording()
    if success:
        return jsonify({"success": True, "file": result, "message": "Recording stopped"}), 200
    return jsonify({"success": False, "error": result}), 400


@camera_bp.route('/status', methods=['GET'])
def handle_status():
    cam_name = request.args.get('camera_name', 'Camera_01')
    # Prefer the full pipeline status (includes per-camera AI detection summary)
    pipeline = camera_manager.get_pipeline(cam_name)
    if pipeline:
        return jsonify(pipeline.get_status()), 200

    stream = camera_manager.get_camera_stream(cam_name)
    if stream:
        return jsonify(stream.get_details()), 200

    return jsonify(camera_manager.get_all_status()), 200


@camera_bp.route('/restart', methods=['POST'])
def handle_restart():
    data = request.get_json() or {}
    cam_name = data.get('camera_name', 'Camera_01')
    
    stream = camera_manager.get_camera_stream(cam_name)
    if stream:
        stream.restart()
        return jsonify({"success": True, "message": f"Camera '{cam_name}' restarting..."}), 200
    return jsonify({"success": False, "error": "Camera not found"}), 404


@camera_bp.route('/add', methods=['POST'])
def handle_add_camera():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    source = data.get('source', '').strip()
    zone = data.get('zone', 'General Area')
    reconnect_delay = int(data.get('reconnect_delay', 5))
    rtsp_transport = data.get('rtsp_transport', 'tcp')
    is_rtsp = int(data.get('is_rtsp', 0))

    if not name or not source:
        return jsonify({"success": False, "error": "Name and source are required."}), 400

    try:
        rtsp_config = {
            "timeout_ms": 5000,
            "buffer_size": 1,
            "transport": rtsp_transport,
            "max_reconnect_delay": 30.0,
            "reconnect_backoff_factor": 1.5,
        }
        pipeline = camera_manager.add_camera(
            name=name,
            ip_url=source,
            zone=zone,
            rtsp_config=rtsp_config,
            reconnect_delay=reconnect_delay,
            auto_start=False
        )
        from database.db import save_camera
        save_camera(
            name=name,
            stream_url=source,
            location=zone,
            status="OFFLINE",
            user_id=_get_current_user_id(),
            is_rtsp=is_rtsp
        )
        return jsonify({"success": True, "message": f"Camera '{name}' added."}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@camera_bp.route('/remove/<path:name>', methods=['DELETE'])
def handle_remove_camera(name):
    try:
        camera_manager.remove_camera(name)
        from database.db import get_connection
        user_id = _get_current_user_id()
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cameras WHERE name = ? AND user_id = ?", (name, user_id))
            conn.commit()
        return jsonify({"success": True, "message": f"Camera '{name}' removed."}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@camera_bp.route('/start/<path:name>', methods=['POST'])
def handle_start_camera(name):
    try:
        pipeline = camera_manager.get_pipeline(name)
        if not pipeline:
            return jsonify({"success": False, "error": "Camera not found."}), 404
        pipeline.start()
        return jsonify({"success": True, "message": f"Camera '{name}' starting."}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@camera_bp.route('/stop/<path:name>', methods=['POST'])
def handle_stop_camera(name):
    try:
        pipeline = camera_manager.get_pipeline(name)
        if not pipeline:
            return jsonify({"success": False, "error": "Camera not found."}), 404
        pipeline.stop()
        return jsonify({"success": True, "message": f"Camera '{name}' stopped."}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@camera_bp.route('/test-connection', methods=['POST'])
def handle_test_connection():
    data = request.get_json() or {}
    source = data.get('source', '').strip()
    if not source:
        return jsonify({"success": False, "error": "Source is required."}), 400

    try:
        import cv2
        target = int(source) if str(source).isdigit() else source
        try:
            cap = cv2.VideoCapture(target, cv2.CAP_DSHOW if sys.platform.startswith("win") else 0)
        except Exception:
            cap = cv2.VideoCapture(target)
        if not cap.isOpened():
            return jsonify({"success": False, "error": "Failed to open camera stream."}), 200

        ret, frame = cap.read()
        cap.release()
        if not ret or frame is None:
            return jsonify({"success": False, "error": "Stream opened but no frame received."}), 200

        h, w = frame.shape[:2]
        return jsonify({
            "success": True,
            "resolution": f"{w}x{h}",
            "fps": 30
        }), 200
    except BaseException as e:
        return jsonify({"success": False, "error": str(e)}), 200
