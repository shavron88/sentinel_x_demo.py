import json

from flask import Blueprint, jsonify, request

from system.monitor import SystemMonitor
from database.db import get_all_events
from api.auth import require_auth, get_current_user_id

system_bp = Blueprint('system_api', __name__)
sys_monitor = SystemMonitor()

MAX_INCIDENT_LIMIT = 500


@system_bp.route('/api/system', methods=['GET'])
@require_auth
def get_system_metrics():
    return jsonify({
        "status": "success",
        "data": sys_monitor.get_metrics()
    })


def _parse_metadata(raw):
    """`events.metadata` is stored as JSON text, so decode it before use.

    The incidents page previously only looked for a dict, so every description
    fell back to the generic template.
    """
    if not raw:
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        decoded = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}
    return decoded if isinstance(decoded, dict) else {}


@system_bp.route('/api/incidents', methods=['GET'])
@require_auth
def get_incidents():
    """Returns recent incidents/events for the incidents page."""
    try:
        user_id = get_current_user_id()
        limit = max(1, min(request.args.get("limit", 50, type=int) or 50, MAX_INCIDENT_LIMIT))
        severity = request.args.get("severity")
        camera = request.args.get("camera")

        events = get_all_events(
            limit=limit,
            user_id=user_id,
            severities=[severity] if severity else None,
            cameras=[camera] if camera else None,
        )

        incidents = []
        for event in events:
            metadata = _parse_metadata(event.get('metadata'))
            default_description = (
                f"{event.get('event_type', 'Unknown event')} detected at "
                f"{event.get('zone', 'unknown location')}"
            )
            description = metadata.get('description') or metadata.get('ai_description') or default_description

            incidents.append({
                "id": event.get('id'),
                "type": event.get('event_type', 'Unknown'),
                "severity": event.get('severity', 'LOW'),
                "zone": event.get('zone', 'Unknown'),
                "time": event.get('timestamp', ''),
                "camera": event.get('camera', 'Unknown'),
                "description": description,
                "confidence": event.get('confidence', 0),
                "duration": event.get('duration', 0),
                "metadata": metadata,
            })
        return jsonify(incidents), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Main loader ke liye alias:
api_bp = system_bp
