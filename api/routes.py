import logging
from flask import Blueprint, jsonify, request
from database.db import get_all_events, get_evidence_by_id

# Blueprint declaration
api_bp = Blueprint("api_bp", __name__)
logger = logging.getLogger("SentinelX.API")


@api_bp.route("/api/events", methods=["GET"])
def get_events_api():
    """Returns list of recent events."""
    limit = request.args.get("limit", 50, type=int)
    events = get_all_events(limit=limit)
    return jsonify({"success": True, "count": len(events), "events": events})


@api_bp.route("/api/evidence/<int:evidence_id>", methods=["GET"])
def get_evidence_api(evidence_id):
    """Returns single evidence record details."""
    evidence = get_evidence_by_id(evidence_id)
    if evidence:
        return jsonify({"success": True, "evidence": evidence})
    return jsonify({"success": False, "error": "Evidence not found"}), 404