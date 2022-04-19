from util.geometry_types import Point, PointList

from collections import defaultdict

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
        self.sampled_points = set([(x, y) for x, y in sampled_points.tolist()])

        # Preprocess all points such that arr[i][j] contains all sampled points within eps pixels
        self.arr = [[set() for _ in range(w)] for _ in range(h)]
        for point in self.sampled_points:
            for i in range(-eps, eps + 1):
                for j in range(-eps, eps + 1):
                    cur_pixel = (point[0] + i, point[1] + j)
                    if self.is_valid_point(cur_pixel):
                        self.arr[cur_pixel[1]][cur_pixel[0]].add(point)

        # print([[len(self.arr[j][i]) for i in range(w)] for j in range(h)])

        # Initialize with a max distance
        max_distance = np.hypot(w, h)
        self.distances = defaultdict(lambda: max_distance)
        self.new_locations = dict()

    def get_points(self, point: Point) -> PointList:
        """Return all sampled points within eps pixels of the given point."""
        return list(self.arr[point[1]][point[0]])

    def unify_with_potrace(self, k: int) -> PointList:
        def read_svg(filename: str) -> np.array:
            """Return an SVG image rasterized as an greyscale numpy array."""
            png = cairosvg.svg2png(url=f"{filename}.svg")
            img = Image.open(io.BytesIO(png)) \
                    .resize((self.w, self.h)) \
                    .convert('L')  # Convert to greyscale
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
        for i in range(k):
            filename = f"img/out{i}"
            img = read_svg(filename)

            # We need to perform edge detection because potrace returns the image in black and white areas
            greyscale = get_edges(img)
            black_pixel_inds = np.argwhere(greyscale > 64)
            # import matplotlib.pyplot as plt
            # plt.imshow(greyscale)
            # plt.scatter([x[1] for x in black_pixel_inds], [x[0] for x in black_pixel_inds], s=1)
            # plt.show()

            print("Number of black pixels:", len(black_pixel_inds))
            for ind in black_pixel_inds:
                x, y = ind
                for sampled_point in self.arr[x][y]:
                    sampled_y, sampled_x = sampled_point

                    # If the current black pixel is closer than any previous black pixel, 
                    # then update the new location for the sampled point
                    dist = np.hypot(sampled_x - x, sampled_y - y)
                    if dist < self.distances[sampled_point]:
                        self.distances[sampled_point] = dist
                        self.new_locations[sampled_point] = ind

        # Update the locations for the sampled points
        for sampled_point, new_point in self.new_locations.items():
            self.sampled_points.remove(sampled_point)
            new_x, new_y = new_point
            self.sampled_points.add((new_y, new_x))

        return np.array([list(x) for x in self.sampled_points]).astype(float)

    def is_valid_point(self, point: Point) -> bool:
        return point[0] >= 0 and point[0] < self.w \
        and point[1] >= 0 and point[1] < self.h
