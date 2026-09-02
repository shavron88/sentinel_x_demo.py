from flask import Blueprint, jsonify
from system.monitor import SystemMonitor
from database.db import get_all_events
from api.auth import require_auth

system_bp = Blueprint('system_api', __name__)
sys_monitor = SystemMonitor()

@system_bp.route('/api/system', methods=['GET'])
@require_auth
def get_system_metrics():
    return jsonify({
        "status": "success",
        "data": sys_monitor.get_metrics()
    })


@system_bp.route('/api/incidents', methods=['GET'])
@require_auth
def get_incidents():
    """Returns recent incidents/events for the incidents page."""
    try:
        events = get_all_events(limit=50)
        incidents = []
        for event in events:
            metadata = event.get('metadata')
            description = "No description available"
            if metadata and isinstance(metadata, dict):
                description = metadata.get('description', description)
            else:
                description = f"{event.get('event_type', 'Unknown event')} detected at {event.get('zone', 'unknown location')}"
            
            incidents.append({
                "id": event.get('id'),
                "type": event.get('event_type', 'Unknown'),
                "severity": event.get('severity', 'LOW'),
                "zone": event.get('zone', 'Unknown'),
                "time": event.get('timestamp', ''),
                "camera": event.get('camera', 'Unknown'),
                "description": description,
                "confidence": event.get('confidence', 0),
                "duration": event.get('duration', 0)
            })
        return jsonify(incidents), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Main loader ke liye alias:
api_bp = system_bp