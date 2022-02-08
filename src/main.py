import cv2
import numpy as np
from sampling.error_dither import ErrorDither
from sampling.importance_map import ImportanceMap
from sampling.triangulate import Triangulate
from util.mesh_to_svg import SVGWriter

from util.settings import Settings

if __name__ == "__main__":
    settings = Settings()
    settings.print()

    im = ImportanceMap()
    ed = ErrorDither()
    dt = Triangulate()

    # Load the input image
    print("Loading image...")
    img = cv2.imread(settings.image)

    # Perform importance map for blue-noise sampling
    print("Performing importance map...")
    importance_map = im.run(settings, img)

    # Perform Floyd-Steinberg error dithering for blue-noise sampling
    print("Performing error diffusion...")
    sampled_points = ed.run(settings, importance_map)

    # Perform Delaunay triangulation
    print("Performing triangulation...")
    triangulated = dt.run(settings, img, sampled_points)

    # Convert mesh to SVG
    sw = SVGWriter(img.shape[1], img.shape[0], 1)
    sw.draw_triangles(settings.output, triangulated)
