class PeopleCounter:

    def __init__(self):

        self.last_side = {}

        self.entered = 0
        self.exited = 0

    def update(self, track_id, y):

        line = 0.65

        current_side = "TOP"

        if y > line:
            current_side = "BOTTOM"

        if track_id not in self.last_side:

            self.last_side[track_id] = current_side
            return

        previous = self.last_side[track_id]

        if previous == "TOP" and current_side == "BOTTOM":

            self.entered += 1

        elif previous == "BOTTOM" and current_side == "TOP":

            self.exited += 1

        self.last_side[track_id] = current_side

    def inside(self):

        return self.entered - self.exited