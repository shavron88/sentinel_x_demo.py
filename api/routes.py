from flask import Blueprint, jsonify
from system.monitor import SystemMonitor

system_bp = Blueprint('system_api', __name__)
sys_monitor = SystemMonitor()

@system_bp.route('/api/system', methods=['GET'])
def get_system_metrics():
    return jsonify({
        "status": "success",
        "data": sys_monitor.get_metrics()
    })

# Main loader ke liye alias:
api_bp = system_bp