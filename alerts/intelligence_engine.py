from datetime import datetime


class IntelligenceEngine:

    def evaluate(self, event, zone, duration, person_count=1):
        score = 0

        if event["type"] == "LINE_CROSSING":
           score += 2


        if event["type"] == "FALL_DETECTED":
            score += 5

        if event["type"] == "CROWD_DETECTED":
            score += 3

        if event["type"] == "RUNNING":
            score += 3

        if event["type"] == "WEAPON_DETECTED":
            score += 8

        hour = datetime.now().hour

        # =========================
        # Night Time
        # =========================
        if hour >= 22 or hour <= 5:
            score += 2

        # =========================
        # Zone
        # =========================
        if zone == "RESTRICTED":
            score += 4

        elif zone == "ENTRY":
            score += 1

        # =========================
        # Loitering
        # =========================
        if duration > 30:
            score += 2

        # =========================
        # Crowd Detection
        # =========================
        if person_count >= 5:
            score += 2

        # =========================
        # Threat Decision
        # =========================
        if score >= 6:
            return "HIGH"

        elif score >= 3:
            return "MEDIUM"

        return "LOW"