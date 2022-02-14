import cv2
import sampler.BN_Sample as Sampler
from sampling.error_dither import ErrorDither
from sampling.importance_map import ImportanceMap
from sampling.triangulate import Triangulate
from util.mesh_to_svg import SVGWriter

from util.settings import Settings
import matplotlib.pyplot as plt

if __name__ == "__main__":
    settings = Settings()
    settings.print()

    im = ImportanceMap()
    ed = ErrorDither()
    dt = Triangulate()
    bn = Sampler.ImageQuasisampler()

    # Load the input image
    print("Loading image...")
    img = cv2.imread(settings.image)

    # Perform importance map for blue-noise sampling
    print("Performing importance map...")
    importance_map = im.run(settings, img)
    print(importance_map)

    # Perform Floyd-Steinberg error dithering for blue-noise sampling
    print("Performing error diffusion...")
    bn.loadImg(importance_map, 100.0)
    sampled_points = bn.getSampledPoints()
    print(sampled_points)
    print(sampled_points.shape)
    x = sampled_points[:, 0]
    y = sampled_points[:, 1]
    plt.scatter(x, y)
    plt.show()

    # Perform Delaunay triangulation
    print("Performing triangulation...")
    triangulated = dt.run(settings, img, sampled_points)

    # Convert mesh to SVG
    sw = SVGWriter(img.shape[1], img.shape[0], 1)
    sw.draw_triangles(settings.output, triangulated)
