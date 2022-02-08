import numpy as np
import cv2
from typing import List, Tuple

from util.geometry_types import PointList, TriangleList
from util.settings import Settings

class Triangulate:
    """
    Perform Delaunay triangulation.
    """

    def _rect_contains(self, rect: Tuple[int, int, int, int], point: Tuple[int, int]) -> bool:
        """Check if the provided point is inside the provided rectangle."""
        # TODO: refactor
        if point[0] < rect[0] or point[0] > rect[2]:
            return False
        elif point[1] < rect[1] or point[1] > rect[3]:
            return False
        return True

    def run(self, settings: Settings, img: np.ndarray, points: PointList) -> TriangleList:
        rect = (0, 0, img.shape[1], img.shape[0])
        subdiv = cv2.Subdiv2D(rect)

        for x in points:
            subdiv.insert(x)

        return subdiv.getTriangleList()

    def run_and_export(self, settings: Settings, img: np.ndarray, points: PointList) -> TriangleList:
        triangle_list = self.run(settings, img, points)
        rect = (0, 0, img.shape[1], img.shape[0])

        # Draw triangulation as lines on top of the diagram
        for t in triangle_list:
            pt1 = (int(t[0]), int(t[1]))
            pt2 = (int(t[2]), int(t[3]))
            pt3 = (int(t[4]), int(t[5]))

            if self._rect_contains(rect, pt1) \
                and self._rect_contains(rect, pt2) \
                and self._rect_contains(rect, pt3):

                cv2.line(img, pt1, pt2, settings.line_color, 1, cv2.LINE_AA, 0)
                cv2.line(img, pt2, pt3, settings.line_color, 1, cv2.LINE_AA, 0)
                cv2.line(img, pt3, pt1, settings.line_color, 1, cv2.LINE_AA, 0)
        cv2.imwrite(settings.output, img)

        return triangle_list