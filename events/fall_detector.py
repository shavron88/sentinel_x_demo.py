class FallDetector:

    def detect(self, results):

        events = []

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                if int(box.cls[0]) != 0:
                    continue

                if box.id is None:
                    continue

                track_id = int(box.id[0])

                coords = box.xyxy[0]

                if hasattr(coords, "tolist"):
                    x1, y1, x2, y2 = map(float, coords.tolist())
                else:
                    x1, y1, x2, y2 = map(float, coords)

                width = x2 - x1
                height = y2 - y1

                # Person appears wider than tall
                if width > height:

                    events.append({

                        "type": "FALL_DETECTED",
                        "track_id": track_id

                    })

        return events