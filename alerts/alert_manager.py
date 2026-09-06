from alerts.intelligence_engine import analyze



class AlertManager:

    def process(self, event):

        event_type = event["type"]
        severity = event.get("severity", "LOW")
        zone = event.get("zone", "SAFE")

        # ==========================
        # Restricted Area Intrusion
        # ==========================
        if zone == "RESTRICTED":

            return {
                "level": "CRITICAL",
                "message": "Restricted Area Intrusion"
            }

        # ==========================
        # Loitering
        # ==========================
        if event_type == "LOITERING":

            return {
                "level": "WARNING",
                "message": "Person loitering"
            }

        # ==========================
        # Person Detection
        # ==========================
        if event_type == "PERSON_DETECTED":

            if severity == "HIGH":
                level = "CRITICAL"

            elif severity == "MEDIUM":
                level = "WARNING"

            else:
                level = "INFO"

            return {
                "level": level,
                "message": "Person detected"
            }

        if event_type == "LINE_CROSSING":

            return {
                "level": "INFO",
                "message": "Line crossed"
            }

        if event_type == "FALL_DETECTED":

            return {
                "level": "CRITICAL",
                "message": "Person may have fallen"
            }

        if event_type == "CROWD_DETECTED":

            return {
                "level": "WARNING",
                "message": "Crowd detected"
            }

        if event_type == "RUNNING":
            return {
                "level": "WARNING",
                "message": "Person running"
            }

        if event_type == "WEAPON_DETECTED":

            return {
                "level": "CRITICAL",
                "message": "Weapon detected"
            }

        event["analysis"] = analyze(event)

        return None