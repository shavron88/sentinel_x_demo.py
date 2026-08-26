import time


class WeaponDetector:

    def __init__(self, cooldown_seconds: float = 30.0):
        self.last_alert_time = {}
        self.cooldown_seconds = cooldown_seconds

    def detect(self, detections):

        events = []
        current_time = time.time()

        for det in detections:

            class_name = det["label"].lower()

            # Future custom model classes
            if class_name in [
                "gun",
                "pistol",
                "rifle",
                "knife"
            ]:

                track_id = det.get("track_id")

                if track_id is not None:
                    last_time = self.last_alert_time.get(track_id, 0.0)
                    if current_time - last_time < self.cooldown_seconds:
                        continue

                    self.last_alert_time[track_id] = current_time

                events.append({

                    "type": "WEAPON_DETECTED",
                    "track_id": track_id

                })

        return events
