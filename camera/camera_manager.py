import cv2
from config import CAMERA_SOURCE


class CameraManager:

    def __init__(self):

        print("[Camera] Starting Camera...")

        # Use DirectShow instead of MSMF (much more reliable on Windows)
        self.cap = cv2.VideoCapture(CAMERA_SOURCE, cv2.CAP_DSHOW)

        if not self.cap.isOpened():
            raise Exception("Unable to open camera.")

        # Camera settings
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        print("[Camera] Camera Connected!")

    def get_frame(self):

        ret, frame = self.cap.read()

        if not ret:
            print("⚠ Failed to read frame")
            return None

        return frame

    def release(self):

        self.cap.release()