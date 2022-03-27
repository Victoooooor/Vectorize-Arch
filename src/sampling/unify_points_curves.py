from util.geometry_types import Point, PointList

import numpy as np
import io
import cairosvg

from PIL import Image
from scipy import ndimage


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
        def read_svg(filename: str) -> np.array:
            """Return an SVG image rasterized as an greyscale numpy array."""
            png = cairosvg.svg2png(url=f"{filename}.svg")
            img = Image.open(io.BytesIO(png)).convert('L')  # Convert to greyscale
            return np.array(img)
        
        def get_edges(img: np.array) -> np.array:
            """Sobel edge detection from: 
            https://stackoverflow.com/a/32301051
            """
            edge_horizontal = ndimage.sobel(img, 0)
            edge_vertical = ndimage.sobel(img, 1)
            return np.hypot(edge_horizontal, edge_vertical)

        # Read SVG based on:
        # https://stackoverflow.com/a/55442505
        potrace_curves = []
        for i in range(k):
            filename = f"img/out{i}"
            img = read_svg(filename)

            # We need to perform edge detection because potrace returns the image in black and white areas
            greyscale = get_edges(img)

            black_pixel_ind = np.argwhere(greyscale == 255)
            potrace_curves.append(black_pixel_ind)
            print(len(black_pixel_ind))
            # import matplotlib.pyplot as plt
            # plt.imshow(greyscale)
            # plt.scatter([x[1] for x in black_pixel_ind], [x[0] for x in black_pixel_ind], s=1)
            # plt.show()

    def is_valid_point(self, point: Point) -> bool:
        return point[0] >= 0 and point[0] < self.w \
        and point[1] >= 0 and point[1] < self.h
