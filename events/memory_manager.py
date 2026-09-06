import time


class MemoryManager:

    def __init__(self):
        self.people = {}

    def update(self, track_id, zone="SAFE"):

        now = time.time()

        if track_id not in self.people:

            self.people[track_id] = {
                "first_seen": now,
                "last_seen": now,
                "duration": 0,
                "visit_count": 1,
                "current_zone": zone,
                "previous_zone": zone
            }

        else:

            person = self.people[track_id]

            person["last_seen"] = now
            person["duration"] = now - person["first_seen"]

            if zone != person["current_zone"]:
                person["previous_zone"] = person["current_zone"]
                person["current_zone"] = zone
                person["visit_count"] += 1

        return self.people[track_id]

    def get_duration(self, track_id):

        if track_id not in self.people:
            return 0

        return self.people[track_id]["duration"]

    def get_zone(self, track_id):

        if track_id not in self.people:
            return "SAFE"

        return self.people[track_id]["current_zone"]

    def get_previous_zone(self, track_id):

        if track_id not in self.people:
            return "SAFE"

        return self.people[track_id]["previous_zone"]

    def moved_to_restricted(self, track_id):

        if track_id not in self.people:
            return False

        person = self.people[track_id]

        return (
            person["previous_zone"] != "RESTRICTED"
            and person["current_zone"] == "RESTRICTED"
        )

    def check_loitering(self, track_id, limit=30):

        return self.get_duration(track_id) >= limit

    def cleanup(self, timeout=10):
        now = time.time()

        remove = []

        for track_id, person in self.people.items():
            if now - person["last_seen"] > timeout:
                remove.append(track_id)

        for track_id in remove:
            del self.people[track_id]