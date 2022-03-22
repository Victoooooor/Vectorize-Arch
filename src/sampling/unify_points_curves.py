from util.geometry_types import Point, PointList

import numpy as np
import io
import cairosvg

from PIL import Image


class Unifier():
    def __init__(self, w: int, h: int, sampled_points: PointList, eps: int = 5) -> None:
        """
        eps:  Maximum number of pixels from a curve for a point to be considered part of the curve
        """
        self.w = w
        self.h = h

        sampled_points = np.floor(sampled_points).astype(int)
        sampled_points = [(x, y) for x, y in sampled_points.tolist()]

        # Preprocess all points such that arr[i][j] contains all sampled points within eps pixels
        self.arr = [[set() for _ in range(w)] for _ in range(h)]
        for point in sampled_points:
            for i in range(-eps, eps + 1):
                for j in range(-eps, eps + 1):
                    cur_pixel = (point[0] + i, point[1] + j)
                    if self.is_valid_point(cur_pixel):
                        self.arr[cur_pixel[1]][cur_pixel[0]].add(point)

        # print([[len(self.arr[j][i]) for i in range(w)] for j in range(h)])

    def get_points(self, point: Point) -> PointList:
        """Return all sampled points within eps pixels of the given point."""
        return list(self.arr[point[1]][point[0]])

    def unify_with_potrace(self, k: int) -> PointList:
        # Read SVG based on:
        # https://stackoverflow.com/a/55442505
        potrace_curves = []
        for i in range(k):
            filename = f"img/out{i}"
            png = cairosvg.svg2png(url=f"{filename}.svg")
            img = np.array(Image.open(io.BytesIO(png)))
            potrace_curves.append(img)
            # print(np.sum(np.sum(img, axis=-1) == 0))
            # import matplotlib.pyplot as plt
            # plt.imshow(img)
            # plt.show()

    def is_valid_point(self, point: Point) -> bool:
        return point[0] >= 0 and point[0] < self.w \
        and point[1] >= 0 and point[1] < self.h
