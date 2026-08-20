import time


class FallDetector:

    def __init__(self, cooldown_seconds: float = 30.0):
        self.last_fall_time = {}
        self.cooldown_seconds = cooldown_seconds

    def detect(self, detections):

        events = []
        current_time = time.time()

        for det in detections:

            if det["class_id"] != 0:
                continue

            track_id = det.get("track_id")
            if track_id is None:
                continue

            x1, y1, x2, y2 = det["bbox"]

            width = x2 - x1
            height = y2 - y1

            # Person appears wider than tall
            if width > height:
                last_time = self.last_fall_time.get(track_id, 0.0)
                if current_time - last_time < self.cooldown_seconds:
                    continue

                self.last_fall_time[track_id] = current_time

                events.append({

                    "type": "FALL_DETECTED",
                    "track_id": track_id

                })

        return events
