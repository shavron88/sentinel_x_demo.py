class LineCrossingDetector:

    def __init__(self):

        self.last_side = {}

    def update(self, track_id, y):

        line = 0.65

        current_side = "TOP"

        if y > line:
            current_side = "BOTTOM"

        if track_id not in self.last_side:

            self.last_side[track_id] = current_side
            return None

        previous = self.last_side[track_id]

        self.last_side[track_id] = current_side

        if previous != current_side:

            return {

                "type": "LINE_CROSSING",
                "track_id": track_id

            }

        return None