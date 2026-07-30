import math


class RunningDetector:

    def __init__(self):

        self.previous = {}

    def update(self, track_id, cx, cy):

        if track_id not in self.previous:

            self.previous[track_id] = (cx, cy)

            return None

        px, py = self.previous[track_id]

        distance = math.sqrt(
            (cx - px) ** 2 +
            (cy - py) ** 2
        )

        self.previous[track_id] = (cx, cy)

        if distance > 0.05:

            return {

                "type": "RUNNING",
                "track_id": track_id

            }

        return None