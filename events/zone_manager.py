import cv2


class ZoneManager:

    def get_zone(self, x, y):
        """
        x and y are normalized coordinates (0.0 - 1.0)
        """

        # Bottom Left
        if y > 0.65 and x < 0.5:
            return "ENTRY"

        # Bottom Right
        if y > 0.65 and x >= 0.5:
            return "RESTRICTED"

        return "SAFE"

    def draw(self, frame):
        """
        Draw security zones on the camera frame.
        """

        h, w = frame.shape[:2]

        line_y = int(h * 0.65)
        center_x = w // 2

        # Horizontal divider
        cv2.line(frame, (0, line_y), (w, line_y), (255, 255, 255), 2)

        # Vertical divider
        cv2.line(frame, (center_x, line_y), (center_x, h), (255, 255, 255), 2)

        # Labels
        cv2.putText(
            frame,
            "ENTRY",
            (30, h - 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            "RESTRICTED",
            (center_x + 20, h - 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

        cv2.putText(
            frame,
            "SAFE",
            (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 0),
            2
        )

        return frame