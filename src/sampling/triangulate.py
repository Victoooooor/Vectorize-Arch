import math
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
    #     """Mean of three vertices colors."""
    #     x1, y1, x2, y2, x3, y3 = t
    #     c = img[int(y1), int(x1)]/3 \
    #         + img[int(y2), int(x2)]/3 \
    #         + img[int(y3), int(x3)]/3
    #     return c[2], c[1], c[0]

    # def _triangle_color(self, img: np.ndarray, t: Tuple[int, int, int, int, int, int]) -> Tuple[int, int, int]:
    #     """Mean of randomly sampled N points."""
    #     N = 10
    #     h, w, _ = img.shape
    #     x1, y1, x2, y2, x3, y3 = t
    #     c = np.array([0, 0, 0])
    #     v1x, v1y = x2 - x1, y2 - y1
    #     v2x, v2y = x3 - x1, y3 - y1
    #     for i in range(N):
    #         u, v = random.random(), random.random()
    #         if u + v > 1:
    #             u = 1 - u
    #         x = max(0, min(w-1, u * v1x + v * v2x + x1))
    #         y = max(0, min(h-1, u * v1y + v * v2y + y1))
    #         c += img[int(y), int(x)]
    #     return c[2]/N, c[1]/N, c[0]/N

    def _triangle_color(self, img: np.ndarray, t: Tuple[int, int, int, int, int, int]) -> Tuple[int, int, int]:
        """Calculate the mean of all points in the triangle. Return an RGB tuple representing the color of the triangle."""
        def plot_triangle(t):
            """Used to debug."""
            import matplotlib.pyplot as plt
            plt.scatter([t[1], t[3], t[5]], [t[0], t[2], t[4]])
            t1 = plt.Polygon([(t[1], t[0]), (t[3], t[2]), (t[5], t[4])])
            plt.gca().add_patch(t1)
            plt.show()

        def vertices_color(img: np.ndarray, t: Tuple[int, int, int, int, int, int]) -> Tuple[int, int, int]:
            """Mean of three vertices colors."""
            x1, y1, x2, y2, x3, y3 = t
            c = img[int(y1), int(x1)]/3 \
                + img[int(y2), int(x2)]/3 \
                + img[int(y3), int(x3)]/3
            return c[::-1]

        pts = self._get_points_in_triangle(t)
        # print(pts)

        # Used in case of very small triangles
        # E.g. (150, 38), (151, 37), (151, 38)
        if len(pts) <= 3:
            return vertices_color(img, t)

        try:
            colors = [img[y][x] for x, y in pts]
        except:
            print(t)
            plot_triangle(t)
            exit()
        # print(colors)
        
        # View each triangle along with the sampled points
        # import matplotlib.pyplot as plt
        # print([(y,x) for x,y in pts])
        # t1 = plt.Polygon([(t[1], t[0]), (t[3], t[2]), (t[5], t[4])], alpha=0.3)
        # plt.gca().add_patch(t1)
        # plt.scatter([y for x,y in pts], [x for x,y in pts], c='red')
        # plt.show()
        # if input() == 'a':
        #     exit()

        # Calculate the mean of the colors
        mean = np.mean(colors, axis=0)
        triangle_color = np.round(mean)

        # Calculate the mode of the colors
        # from scipy import stats
        # mode, _ = stats.mode(colors, axis=0)
        # triangle_color = mode[0]

        # We return the reversed color because cv2 uses BGR
        return triangle_color[::-1]

    def _get_points_in_triangle(self, t: Tuple[int, int, int, int, int, int]) -> PointList:
        """Based on:
        http://www.sunshine2k.de/coding/java/TriangleRasterization/TriangleRasterization.html
        """
        # Pack triangle into tuples for sorting
        t = [int(x) for x in t]
        triangle = [(t[0], t[1]), (t[2], t[3]), (t[4], t[5])]

        # Sort by y
        sorted_triangle = sorted(triangle, key = lambda x: x[1])
        (x1, y1), (x2, y2), (x3, y3) = sorted_triangle

        def get_bottom_flat_triangle_points(x1: int, y1: int, x2: int, y2: int, x3: int, y3: int) -> PointList:
            slope_1 = (x2 - x1) / (y2 - y1)
            slope_2 = (x3 - x1) / (y3 - y1)

            points = []
            cur_x1 = x1
            cur_x2 = x1
            for y in range(y1, y2 + 1):
                point_x1 = math.floor(cur_x1)
                point_x2 = math.floor(cur_x2)

                points += [(x, y) for x in range(point_x1, point_x2 + 1)]
                cur_x1 += slope_1
                cur_x2 += slope_2

            return points

        def get_top_flat_triangle_points(x1: int, y1: int, x2: int, y2: int, x3: int, y3: int) -> PointList:
            slope_1 = (x3 - x1) / (y3 - y1)
            slope_2 = (x3 - x2) / (y3 - y2)

            points = []
            cur_x1 = x3
            cur_x2 = x3
            for y in reversed(range(y1, y3 + 1)):
                point_x1 = math.floor(cur_x1)
                point_x2 = math.floor(cur_x2)

                points += [(x, y) for x in range(point_x1, point_x2 + 1)]
                cur_x1 -= slope_1
                cur_x2 -= slope_2

            return points

        if y2 == y3:
            pts = get_bottom_flat_triangle_points(x1, y1, x2, y2, x3, y3)
        elif y1 == y2:
            pts = get_top_flat_triangle_points(x1, y1, x2, y2, x3, y3)
        else:
            # Calculate a vertex to split the triangle into two triangles
            # One is top-flat and the other is bottom-flat
            new_vertex_x = (y2 - y1) / (y3 - y1) * (x3 - x1)
            new_vertex_y = y2

            pts = []
            pts += get_bottom_flat_triangle_points(x1, y1, x2, y2, new_vertex_x, new_vertex_y)
            pts += get_top_flat_triangle_points(x2, y2, new_vertex_x, new_vertex_y, x3, y3)

        return pts

    def _triangle_from_points(self, img: np.ndarray, t: Tuple[int, int, int, int, int, int]) -> Triangle:
        """
        Generate a Triangle from the set of points. E.g., calculates the
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
