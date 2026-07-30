from ultralytics import YOLO


class Detector:

    def __init__(self):
        print("[AI] Loading model...")
        self.model = YOLO("models/yolov8m.pt")
        print("[AI] Model loaded!")

    def detect(self, frame):

        results = self.model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False
        )

        return results