from util.settings import Settings
from svgpathtools import svg2paths, wsvg


class PathAnalyzer:
    """
    Decompose the SVG output of potrace into a set of curves to use
    to simplify the point cloud.
    """

    def run(self, settings: Settings) -> None:
        paths, attributes = svg2paths('img/out2.svg')

        total_curves = sum([len(path) for path in paths])
        print(total_curves)

        path = paths[0]
        path_attributes = attributes[0]

        # print(len(path))
        # print(path)
        # print(path_attributes)
        # print(len(paths))
