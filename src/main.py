from cgi import print_directory
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

from util.svg_to_png import PNGWriter

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

    h, w, _ = image.shape

    # # TESTING PATH PARSING
    # pa = PathAnalyzer()
    # pa.run(settings)
    # sys.exit(0)

    # Perform importance map for blue-noise sampling
    print("Performing importance map...")
    im = ImportanceMap()
    importance_map = im.run(settings, image, 1)

    cv2.imwrite("img/im.png", importance_map)

    # # Perform Floyd-Steinberg error dithering for blue-noise sampling
    # print("Performing error diffusion...")
    # ed = ErrorDither()

    print("Sampling points using quasisampler BNS...")
    bn = Sampler.ImageQuasisampler()
    bn.loadImg(importance_map, 100.0)
    # bn.loadPGM('image.pgm', 100.0)
    sampled = bn.getSampledPoints()

    # TESTING AUGMENTING IMAGE WITH STRONG GRADIENT POINTS
    # get importance map as grayscale
    # https://stackoverflow.com/a/596243/2397327
    importance_map_gray = np.sum(
        np.array([0.2126, 0.7152, 0.0722]).reshape((1, 1, -1)) 
        * importance_map, axis=-1) 
    # threshold importance map
    importance_map_gray = np.argwhere(importance_map_gray > 32)
    importance_map_samples = importance_map_gray.shape[0]
    importance_map_gray_samples_i = np.random.choice(
        importance_map_samples,
        size=importance_map_samples // 100,
        replace=False)
    importance_map_gray_samples = importance_map_gray[importance_map_gray_samples_i]
    # switch columns
    importance_map_gray_samples = importance_map_gray_samples[:,::-1]
    print(f"Got {importance_map_gray_samples.shape[0]} strong gradient samples")

    # Export sampled strong points
    importance_map_gray_samples_export = np.zeros((h, w))
    for i, j in importance_map_gray_samples:
        importance_map_gray_samples_export[j, i] = 255
    cv2.imwrite("img/strong_samples.png", importance_map_gray_samples_export)

    print("Performing decimation...")
    md = Decimate()
    sampled = md.run(image, sampled, 10)

    # TESTING COLOR QUANTIZATION
    k = 4
    print(f"Color quantization with k={k}")
    cq = ColorQuantization()
    cq.run_and_export(settings, image, k)

    print("Merging sampled points with Potrace output...")
    up = Unifier(w, h, sampled, 20)
    sampled = up.unify_with_potrace(k)

    # Generate points around the edges
    a = np.linspace(0, w-1, 100)[:, np.newaxis]
    b = np.linspace(0, h-1, 100)[:, np.newaxis]
    left = a * np.array([[1, 0]])
    right = a * np.array([[1, 0]]) + np.array([[0, h-1]])
    top = b * np.array([[0, 1]])
    bottom = b * np.array([[0, 1]]) + np.array([[w-1, 0]])
    sampled = np.concatenate((sampled, left, right, top, bottom))

    print("Concatenating with points sampled from strong gradient")
    sampled = np.concatenate((sampled, importance_map_gray_samples))

    print("Performing triangulation...")
    dt = Triangulate()
    triangulated = dt.run(None, image, sampled.astype(float))

    # Convert mesh to SVG
    sw = SVGWriter(image.shape[1], image.shape[0], 1)
    sw.draw_triangles(settings.output, triangulated)

    # Also export to PNG (later: change this to export to SVG
    # or PNG based on file extension)
    pw = PNGWriter(w, h)
    pw.run(settings)