import cv2
import sampler.BN_Sample as Sampler
from sampling.importance_map import ImportanceMap
from sampling.sampled_points import SampledPoints
from sampling.unify_points_curves import Unifier
from sampling.triangulate import Triangulate
from tracer.color_quant import ColorQuantization
from tracer.path_analysis import PathAnalyzer
from util.mesh_to_svg import SVGWriter
from mesh.decimation import Decimate
from util.settings import Settings
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import sys

sys.path.append('..')


def save_points_to_file(filename: str, x: np.ndarray, y: np.ndarray):
    """Plot and save points without frames or axes."""
    fig = plt.figure(frameon=False)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    ax.invert_yaxis()
    fig.add_axes(ax)

    ax.scatter(x, y, c='black', s=1)
    fig.savefig(filename)


if __name__ == "__main__":
    settings = Settings()
    settings.print()

    # Load the input image
    print("Loading image...")
    image = cv2.imread(settings.image)

    # # TESTING PATH PARSING
    # pa = PathAnalyzer()
    # pa.run(settings)
    # sys.exit(0)

    # # TESTING COLOR QUANTIZATION
    k = 4
    print(f"Color quantization with k={k}")
    cq = ColorQuantization()
    cq.run_and_export(settings, image, k)
    # sys.exit(0)

    # Perform importance map for blue-noise sampling
    print("Performing importance map...")
    im = ImportanceMap()
    importance_map = im.run(settings, image, 1)

    # # Perform Floyd-Steinberg error dithering for blue-noise sampling
    # print("Performing error diffusion...")
    # ed = ErrorDither()

    print("Sampling points using quasisampler BNS...")
    bn = Sampler.ImageQuasisampler()
    bn.loadImg(importance_map, 1000.0)
    # bn.loadPGM('image.pgm', 100.0)
    sampled = bn.getSampledPoints()

    print("Performing decimation...")
    md = Decimate()
    sampled = md.run(image, sampled, 10)

    print("Merging sampled points with Potrace output...")
    h, w, _ = image.shape
    up = Unifier(w, h, sampled, 15)
    sampled = up.unify_with_potrace(k)
    # sys.exit(0)

    # TODO: perform combination algorithm b/t potrace and sampled points
    # sampled = np.array(sp.to_coords())

    print("Performing triangulation...")
    dt = Triangulate()
    triangulated = dt.run(None, image, sampled.astype(float))

    # Convert mesh to SVG
    sw = SVGWriter(image.shape[1], image.shape[0], 1)
    sw.draw_triangles(settings.output, triangulated)
