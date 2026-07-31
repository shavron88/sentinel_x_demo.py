class WeaponDetector:

    def detect(self, results):

        events = []

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                class_id = int(box.cls[0])
                class_name = result.names[class_id].lower()

                # Future custom model classes
                if class_name in [
                    "gun",
                    "pistol",
                    "rifle",
                    "knife"
                ]:

                    if box.id is None:
                        track_id = None
                    else:
                        track_id = int(box.id[0])

                    events.append({

                        "type": "WEAPON_DETECTED",
                        "track_id": track_id

                    })

        return events