import time


class CrowdDetector:

    def __init__(self, threshold: int = 5, cooldown_seconds: float = 60.0):
        self.threshold = threshold
        self.cooldown_seconds = cooldown_seconds
        self.last_alert_time = 0.0

    def detect(self, person_count):

        if person_count >= self.threshold:
            current_time = time.time()
            if current_time - self.last_alert_time < self.cooldown_seconds:
                return None

            self.last_alert_time = current_time

            return {
                "type": "CROWD_DETECTED",
                "severity": "MEDIUM",
                "track_id": None
            }

        return None
