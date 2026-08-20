import time
from config import EVENT_COOLDOWN


class EventManager:

    def __init__(self):
        self.last_event_time = {}
        self.fallback_id = 0

    def process(self, detections):

        events = []
        current_time = time.time()

        for det in detections:

            class_id = det["class_id"]
            class_name = det["label"]
            confidence = det["confidence"]

            if class_name != "person":
                continue

            # =========================
            # FIX: SAFE TRACK ID
            # =========================
            track_id = det.get("track_id")
            if track_id is None:
                self.fallback_id += 1
                track_id = self.fallback_id

            event_type = "PERSON_DETECTED"

            last_time = self.last_event_time.get(track_id, 0)

            if current_time - last_time >= EVENT_COOLDOWN:

                self.last_event_time[track_id] = current_time

                events.append({
                    "type": event_type,
                    "track_id": track_id,
                    "confidence": round(confidence, 2)
                })

        return events
