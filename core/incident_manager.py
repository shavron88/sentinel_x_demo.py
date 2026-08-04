from datetime import datetime


class IncidentManager:

    def __init__(self):

        self.incidents = []

    def add_incident(
        self,
        incident_type,
        severity,
        zone,
        track_id=None,
        confidence=None
    ):

        incident = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "type": incident_type,
            "severity": severity,
            "zone": zone,
            "track_id": track_id,
            "confidence": confidence
        }

        self.incidents.insert(0, incident)

        # Keep latest 100 incidents
        self.incidents = self.incidents[:100]

        print(
            f"[INCIDENT] "
            f"{incident['time']} | "
            f"{incident_type} | "
            f"{severity} | "
            f"{zone}"
        )

    def get_incidents(self):
        return self.incidents

    def clear(self):
        self.incidents.clear()