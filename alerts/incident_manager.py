import time


class IncidentManager:

    def __init__(self):

        self.current_incident = None

        self.timeout = 15

    def update(self, event):

        now = time.time()

        if self.current_incident is None:

            self.current_incident = {
                "start_time": now,
                "last_activity": now,
                "events": [event],
                "severity": event.get("severity", "LOW")
            }

            return self.current_incident

        if now - self.current_incident["last_activity"] <= self.timeout:

            self.current_incident["last_activity"] = now
            self.current_incident["events"].append(event)

            if event.get("severity") == "HIGH":
                self.current_incident["severity"] = "HIGH"

            elif (
                event.get("severity") == "MEDIUM"
                and self.current_incident["severity"] == "LOW"
            ):
                self.current_incident["severity"] = "MEDIUM"

            return self.current_incident

        incident = self.current_incident

        self.current_incident = {
            "start_time": now,
            "last_activity": now,
            "events": [event],
            "severity": event.get("severity", "LOW")
        }

        return incident

    def get_current(self):

        return self.current_incident