from datetime import datetime


class RuleEngine:

    def evaluate(self, event, track_id):

        hour = datetime.now().hour

        event_type = event["type"]

        # Default severity
        severity = "INFO"
        message = "Normal activity detected"

        # Rule 1: Night time escalation
        if hour >= 22 or hour <= 5:
            severity = "WARNING"
            message = "Activity detected during night hours"

        # Rule 2: Crowd / multiple detection (future expand)
        if "CROWD" in event_type:
            severity = "CRITICAL"
            message = "Crowd detected - security risk"

        # Rule 3: Person detection baseline
        if event_type == "PERSON_DETECTED":
            severity = "INFO"
            message = f"Person detected (ID: {track_id})"

        return {
            "severity": severity,
            "message": message
        }