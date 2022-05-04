# Basic blue-noise sampling without other heuristics

import cv2

import sampler.BN_Sample as Sampler
from sampling.importance_map import ImportanceMap
from sampling.triangulate import Triangulate
from util.mesh_to_svg import SVGWriter
from util.settings import Settings
from util.svg_to_png import PNGWriter
from util.vectorization_driver import VectorizationDriver


class PlainBNSDriver(VectorizationDriver):

    def get_name(self) -> str:
        return 'bns'

    def run(self):
        # Load the input image
        print("Loading image...")
        image = cv2.imread(self.settings.image)

        h, w, _ = image.shape

        # Perform importance map for blue-noise sampling
        print("Performing importance map...")
        im = ImportanceMap()
        importance_map = im.run(self.settings, image, 1)

        # Perform BNS
        print("Sampling points using quasisampler BNS...")
        bn = Sampler.ImageQuasisampler()
        bn.loadImg(importance_map, 100.0)
        sampled = bn.getSampledPoints()

        # Triangulate (and color)
        print("Performing triangulation...")
        dt = Triangulate()
        triangulated = dt.run(None, image, sampled.astype(float))

        # Convert mesh to SVG
        sw = SVGWriter(w, h, 1)
        sw.draw_triangles(self.settings.output, triangulated)

        # Also export to PNG
        pw = PNGWriter(w, h)
        pw.run(self.settings)

if __name__ == '__main__':
    settings = Settings()
    settings.print()

    PlainBNSDriver(settings).run()