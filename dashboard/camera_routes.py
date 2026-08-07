from flask import Blueprint, jsonify, request
from camera.camera_manager import camera_manager

camera_bp = Blueprint('camera', __name__, url_prefix='/api/camera')

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