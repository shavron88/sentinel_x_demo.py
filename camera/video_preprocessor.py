import cv2
import numpy as np
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger("SentinelX.VideoPreprocessor")


class VideoPreprocessor:
    """Preprocesses video frames to normalize camera perspective.

    Applies frame-level transformations so that videos from varied sources
    can be presented in a consistent surveillance/camera viewpoint:
    - Resize to standard resolution
    - Normalize brightness/contrast
    - Optional timestamp overlay to reinforce CCTV-style perspective
    - Optional border/letterbox to enforce aspect ratio
    """

    def __init__(
        self,
        target_width: int = 1280,
        target_height: int = 720,
        normalize_color: bool = True,
        add_timestamp: bool = False,
        enforce_aspect_ratio: bool = True,
    ):
        self.target_width = target_width
        self.target_height = target_height
        self.normalize_color = normalize_color
        self.add_timestamp = add_timestamp
        self.enforce_aspect_ratio = enforce_aspect_ratio

    def process(self, frame):
        """Apply preprocessing to a single frame."""
        if frame is None:
            return None

        h, w = frame.shape[:2]

        # Resize to target resolution if needed
        if w != self.target_width or h != self.target_height:
            frame = cv2.resize(frame, (self.target_width, self.target_height), interpolation=cv2.INTER_AREA)

        # Normalize brightness/contrast to surveillance-friendly levels
        if self.normalize_color:
            frame = self._normalize_color(frame)

        # Add timestamp overlay to reinforce camera perspective
        if self.add_timestamp:
            frame = self._add_timestamp(frame)

        # Enforce aspect ratio with letterboxing if needed
        if self.enforce_aspect_ratio:
            frame = self._enforce_aspect_ratio(frame)

        return frame

    def _normalize_color(self, frame):
        """Apply CLAHE and mild contrast normalization."""
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        frame = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        # Mild gamma correction for consistent brightness
        gamma = 1.2
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(256)]).astype("uint8")
        frame = cv2.LUT(frame, table)
        return frame

    def _add_timestamp(self, frame):
        """Overlay a CCTV-style timestamp in the top-right corner."""
        h, w = frame.shape[:2]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text_size, _ = cv2.getTextSize(timestamp, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        text_w = text_size[0] + 20
        text_h = text_size[1] + 20
        x = w - text_w - 10
        y = 10 + text_h
        cv2.rectangle(frame, (x, 10), (x + text_w, y), (0, 0, 0), -1)
        cv2.putText(frame, timestamp, (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        return frame

    def _enforce_aspect_ratio(self, frame):
        """Letterbox to 16:9 if the frame deviates."""
        h, w = frame.shape[:2]
        target_ar = self.target_width / self.target_height
        current_ar = w / h
        if abs(current_ar - target_ar) < 0.02:
            return frame

        if current_ar > target_ar:
            new_w = int(h * target_ar)
            x = (w - new_w) // 2
            frame = frame[:, x:x + new_w]
        else:
            new_h = int(w / target_ar)
            y = (h - new_h) // 2
            frame = frame[y:y + new_h, :]

        if frame.shape[:2] != (self.target_height, self.target_width):
            frame = cv2.resize(frame, (self.target_width, self.target_height), interpolation=cv2.INTER_AREA)

        return frame
