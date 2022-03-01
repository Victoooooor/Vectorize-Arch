import cv2
import sampler.BN_Sample as Sampler
from sampling.importance_map import ImportanceMap
from sampling.triangulate import Triangulate
from tracer.color_quant import ColorQuantization
from util.mesh_to_svg import SVGWriter
from mesh.decimation import Decimate
from util.settings import Settings
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import sys

sys.path.append('..')
if __name__ == "__main__":
    settings = Settings()
    settings.print()

    im = ImportanceMap()
    # ed = ErrorDither()
    dt = Triangulate()
    bn = Sampler.ImageQuasisampler()
    cq = ColorQuantization()

    # Load the input image
    print("Loading image...")
    image = cv2.imread(settings.image)

    # # TESTING COLOR QUANTIZATION
    # k = 4
    # print(f"Color quantization with k={k}")
    # cq.run_and_export(settings, image, k)
    # sys.exit(0)

    # Perform importance map for blue-noise sampling
    print("Performing importance map...")
    im = ImportanceMap()
    dt = Triangulate()
    md = Decimate()
    print("Performing error diffusion...")
    importance_map = im.run(None, image, 0.5)

    Sampler = Sampler.ImageQuasisampler()
    Sampler.loadImg(importance_map, 1000.0)
    # Sampler.loadPGM('image.pgm', 100.0)
    Sampled = Sampler.getSampledPoints()
    x = Sampled[:, 0]
    y = Sampled[:, 1]

    newpts = md.run(image, Sampled, 10)
    print("Performing triangulation...")
    triangulated = dt.run(None, image, newpts.astype(float))
    # Perform Floyd-Steinberg error dithering for blue-noise sampling

    # Convert mesh to SVG
    sw = SVGWriter(image.shape[1], image.shape[0], 1)
    sw.draw_triangles(settings.output, triangulated)
