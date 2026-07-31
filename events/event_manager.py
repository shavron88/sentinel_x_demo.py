import time
from config import EVENT_COOLDOWN


class EventManager:

    def __init__(self):
        self.last_event_time = {}
        self.fallback_id = 0

    def process(self, results):

        events = []
        current_time = time.time()

        for result in results:

            boxes = result.boxes

            if boxes is None:
                continue

            for box in boxes:

                class_id = int(box.cls[0])
                class_name = result.names[class_id]
                confidence = float(box.conf[0])

                if class_name != "person":
                    continue

                # =========================
                # FIX: SAFE TRACK ID
                # =========================
                if box.id is None or len(box.id) == 0:
                    self.fallback_id += 1
                    track_id = self.fallback_id
                else:
                    track_id = int(box.id[0])

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