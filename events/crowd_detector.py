class CrowdDetector:

    def __init__(self, threshold=5):
        self.threshold = threshold

    def detect(self, person_count):

        if person_count >= self.threshold:

            return {
                "type": "CROWD_DETECTED",
                "severity": "MEDIUM",
                "track_id": None
            }

        return None