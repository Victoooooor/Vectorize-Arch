import numpy as np
import cv2
from typing import Tuple

from util.geometry_types import PointList, Triangle, TriangleList
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

    # def _triangle_color(self, img: np.ndarray, t: Tuple[int, int, int, int, int, int]) -> Tuple[int, int, int]:
    #     """
    #     Mean of three vertices colors
    #     """
    #     x1, y1, x2, y2, x3, y3 = t
    #     c = img[int(y1), int(x1)]/3 \
    #         + img[int(y2), int(x2)]/3 \
    #         + img[int(y3), int(x3)]/3
    #     return c[2], c[1], c[0]

    def _triangle_color(self, img: np.ndarray, t: Tuple[int, int, int, int, int, int]) -> Tuple[int, int, int]:
        """
        Mean of randomly sampled N points
        """
        N = 10
        h, w, _ = img.shape
        x1, y1, x2, y2, x3, y3 = t
        c = np.array([0, 0, 0])
        v1x, v1y = x2 - x1, y2 - y1
        v2x, v2y = x3 - x1, y3 - y1
        for i in range(N):
            u, v = random.random(), random.random()
            if u + v > 1:
                u = 1 - u
            x = max(0, min(w-1, u * v1x + v * v2x + x1))
            y = max(0, min(h-1, u * v1y + v * v2y + y1))
            c += img[int(y), int(x)]
        return c[2]/N, c[1]/N, c[0]/N

    def _triangle_from_points(self, img: np.ndarray, t: Tuple[int, int, int, int, int, int]) -> Triangle:
        """
        Generates a Triangle from the set of points. E.g., calculates the
        triangle color and other attributes.
        """
        x1, y1, x2, y2, x3, y3 = t
        r, g, b = self._triangle_color(img, t)
        return (x1, y1, x2, y2, x3, y3, r, g, b)

    def run(self, settings: Settings, img: np.ndarray, points: PointList) -> TriangleList:
        rect = (0, 0, img.shape[1], img.shape[0])
        subdiv = cv2.Subdiv2D(rect)

        for x in points:
            subdiv.insert(x)

        return [self._triangle_from_points(img, t)
                for t in subdiv.getTriangleList()]

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
