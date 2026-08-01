import cv2
<<<<<<< HEAD
import time
import logging
from config import CAMERA_SOURCE

# Error logs save honge logs/system.log me
logging.basicConfig(
    filename="logs/system.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

=======
from config import CAMERA_SOURCE

>>>>>>> 2ad808518949971ad8ab73951416556e7319fb7e

class CameraManager:

    def __init__(self):

        print("[Camera] Starting Camera...")
<<<<<<< HEAD
        self.connect_camera()

    def connect_camera(self):

        self.cap = cv2.VideoCapture(CAMERA_SOURCE, cv2.CAP_DSHOW)

        if not self.cap.isOpened():
            print("[Camera] Unable to open camera.")
            logging.error("Unable to open camera.")
            return

=======

        # Use DirectShow instead of MSMF (much more reliable on Windows)
        self.cap = cv2.VideoCapture(CAMERA_SOURCE, cv2.CAP_DSHOW)

        if not self.cap.isOpened():
            raise Exception("Unable to open camera.")

        # Camera settings
>>>>>>> 2ad808518949971ad8ab73951416556e7319fb7e
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        print("[Camera] Camera Connected!")

<<<<<<< HEAD
    def reconnect(self):

        print("[Camera] Reconnecting...")

        if self.cap:
            self.cap.release()

        time.sleep(2)

        self.connect_camera()

    def get_frame(self):

        if not self.cap or not self.cap.isOpened():
            logging.error("Camera disconnected. Trying to reconnect.")
            self.reconnect()
            return None

        ret, frame = self.cap.read()

        if not ret:
            print("[Camera] Failed to read frame.")
            logging.error("Camera frame read failed.")
            self.reconnect()
=======
    def get_frame(self):

        ret, frame = self.cap.read()

        if not ret:
            print("⚠ Failed to read frame")
>>>>>>> 2ad808518949971ad8ab73951416556e7319fb7e
            return None

        return frame

    def release(self):

<<<<<<< HEAD
        if self.cap:
            self.cap.release()
=======
        self.cap.release()
>>>>>>> 2ad808518949971ad8ab73951416556e7319fb7e
