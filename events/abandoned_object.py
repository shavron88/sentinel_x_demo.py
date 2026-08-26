import time
import math


class AbandonedObjectDetector:

    def __init__(self):

        self.objects = {}

        # COCO classes
        # backpack = 24
        # handbag = 26
        # suitcase = 28
        self.allowed_classes = [24, 26, 28]

        self.distance_threshold = 35      # pixels
        self.abandon_time = 20            # seconds

    def update(self, detections):

        events = []

        current_time = time.time()

        for det in detections:

            cls = det["class_id"]

            if cls not in self.allowed_classes:
                continue

            track_id = det.get("track_id")
            if track_id is None:
                continue

            x1, y1, x2, y2 = det["bbox"]

            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2

            if track_id not in self.objects:

                self.objects[track_id] = {
                    "x": cx,
                    "y": cy,
                    "start_time": current_time,
                    "last_move": current_time,
                    "alerted": False
                }

                continue

            obj = self.objects[track_id]

            distance = math.sqrt(
                (cx - obj["x"]) ** 2 +
                (cy - obj["y"]) ** 2
            )

            if distance > self.distance_threshold:

                obj["x"] = cx
                obj["y"] = cy
                obj["last_move"] = current_time
                obj["alerted"] = False

            stationary_time = current_time - obj["last_move"]

            if (
                stationary_time >= self.abandon_time
                and not obj["alerted"]
            ):

                obj["alerted"] = True

                events.append({

                    "type": "ABANDONED_OBJECT",
                    "track_id": track_id,
                    "duration": int(stationary_time)

                })

        return events
