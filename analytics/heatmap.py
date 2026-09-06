import cv2
import numpy as np


class Heatmap:

    def __init__(self):

        self.map = np.zeros((360, 640), dtype=np.float32)

    def update(self, x, y):

        x = int(x)
        y = int(y)

        cv2.circle(
            self.map,
            (x, y),
            25,
            1,
            -1
        )

    def render(self):

        normalized = cv2.normalize(
            self.map,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        )

        normalized = normalized.astype(np.uint8)

        return cv2.applyColorMap(
            normalized,
            cv2.COLORMAP_JET
        )