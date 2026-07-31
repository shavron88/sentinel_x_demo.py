import cv2
import os
from datetime import datetime

saved_images = []


class EvidenceManager:

    def __init__(self):

        self.folder = "evidence/screenshots"

        os.makedirs(self.folder, exist_ok=True)

        # Keeps track of captured incidents
        self.saved_incidents = set()

    def save(self, frame, event_type, track_id=None):

        # Unique incident key
        key = f"{event_type}_{track_id}"

        # Already saved for this person
        if track_id is not None and key in self.saved_incidents:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        filename = f"{event_type}_{track_id}_{timestamp}.jpg"

        filepath = os.path.join(
            self.folder,
            filename
        )

        cv2.imwrite(filepath, frame)

        print(f"[Evidence] Saved -> {filename}")

        saved_images.insert(0, filename)

        if len(saved_images) > 30:
            saved_images.pop()

        if track_id is not None:
            self.saved_incidents.add(key)

    def reset(self, event_type, track_id):

        key = f"{event_type}_{track_id}"

        if key in self.saved_incidents:
            self.saved_incidents.remove(key)


def get_gallery():

    return saved_images