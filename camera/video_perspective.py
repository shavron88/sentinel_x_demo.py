import cv2
import os
import logging
import numpy as np
from typing import Tuple, Optional

logger = logging.getLogger("SentinelX.VideoPerspective")

# Typical surveillance camera characteristics
SURVEILLANCE_RESOLUTIONS = [
    (640, 480), (1280, 720), (1920, 1080),
    (704, 576), (352, 288), (1280, 960)
]

SURVEILLANCE_FPS_RANGE = (1.0, 60.0)
SURVEILLANCE_MIN_EDGE_DENSITY = 10.0
SURVEILLANCE_MAX_AVG_MOTION = 20.0


class VideoPerspectiveValidator:
    """Validates whether a video appears to be captured from a surveillance
    camera perspective using OpenCV heuristics.

    Heuristics:
    - Resolution matches common surveillance standards
    - Frame rate is within surveillance range
    - Low average motion (fixed camera)
    - Edge density consistent with structured scenes
    - Corner uniformity (CCTV often has timestamp/watermark in corners)
    """

    def __init__(
        self,
        resolutions: list = None,
        fps_range: Tuple[float, float] = None,
        min_edge_density: float = None,
        max_avg_motion: float = None,
    ):
        self.resolutions = resolutions or SURVEILLANCE_RESOLUTIONS
        self.fps_range = fps_range or SURVEILLANCE_FPS_RANGE
        self.min_edge_density = min_edge_density if min_edge_density is not None else SURVEILLANCE_MIN_EDGE_DENSITY
        self.max_avg_motion = max_avg_motion if max_avg_motion is not None else SURVEILLANCE_MAX_AVG_MOTION

    def validate(self, filepath: str) -> Tuple[bool, dict]:
        """Return (is_camera_perspective, metadata)."""
        meta = {
            "resolution": None,
            "fps": None,
            "frame_count": 0,
            "avg_motion": 0.0,
            "edge_density": 0.0,
            "corner_uniformity": 0.0,
            "reasons": [],
        }

        if not os.path.isfile(filepath):
            meta["reasons"].append("file_not_found")
            return False, meta

        cap = cv2.VideoCapture(filepath)
        if not cap.isOpened():
            meta["reasons"].append("cannot_open")
            return False, meta

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        meta["resolution"] = f"{width}x{height}"
        meta["fps"] = round(float(fps), 2) if fps else 0.0
        meta["frame_count"] = frame_count

        if frame_count < 2:
            meta["reasons"].append("insufficient_frames")
            cap.release()
            return False, meta

        frames = []
        for i in range(min(10, frame_count)):
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
        cap.release()

        if not frames:
            meta["reasons"].append("no_readable_frames")
            return False, meta

        first = frames[0]
        gray = cv2.cvtColor(first, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # Edge density
        edges = cv2.Canny(gray, 50, 150)
        edge_density = float(edges.mean())
        meta["edge_density"] = round(edge_density, 2)

        # Corner uniformity (CCTV often has timestamp/watermark)
        corners = [
            gray[0:h//4, 0:w//4],
            gray[0:h//4, 3*w//4:w],
            gray[3*h//4:h, 0:w//4],
            gray[3*h//4:h, 3*w//4:w]
        ]
        corner_means = [float(c.mean()) for c in corners]
        corner_uniformity = float(np.std(corner_means))
        meta["corner_uniformity"] = round(corner_uniformity, 2)

        # Average motion
        if len(frames) > 1:
            diffs = []
            for i in range(1, min(5, len(frames))):
                diff = cv2.absdiff(frames[i], frames[i-1])
                diffs.append(float(diff.mean()))
            avg_motion = float(np.mean(diffs))
        else:
            avg_motion = 0.0
        meta["avg_motion"] = round(avg_motion, 2)

        # Apply heuristics
        score = 0
        max_score = 4

        if (width, height) in self.resolutions:
            score += 1
        else:
            meta["reasons"].append("non_standard_resolution")

        if self.fps_range[0] <= fps <= self.fps_range[1]:
            score += 1
        else:
            meta["reasons"].append("fps_out_of_range")

        if avg_motion <= self.max_avg_motion:
            score += 1
        else:
            meta["reasons"].append("high_motion")

        if edge_density >= self.min_edge_density:
            score += 1
        else:
            meta["reasons"].append("low_edge_density")

        # Require at least 3/4 heuristics to pass
        is_camera = score >= 3
        meta["score"] = score
        meta["max_score"] = max_score

        return is_camera, meta
