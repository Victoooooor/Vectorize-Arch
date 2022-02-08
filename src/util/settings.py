import argparse

from util.geometry_types import Color

class Settings:

    def __init__(self):
        # Construct the argument parser and parse the arguments
        ap = argparse.ArgumentParser()
        ap.add_argument("-i", "--image", required=True, help="path to input image")
        ap.add_argument("-o", "--output", required=True, help="path to outputs")
        ap.add_argument("-sf", "--samplingf",
            required=False, const=1.0, type=float, nargs='?', default=1.0,
            help="sampling_f value for Floyd-Steinberg dithering")
        ap.add_argument("-b", "--bench",
            required=False, const=False, type=bool, nargs='?', default=False,
            help="time each stage of the algorithm")
        ap.add_argument("-lc", "--linecolor",
            required=False, type=Color, nargs='+', default=(255,255,255),
            help="color of mesh lines")
        settings_dict = vars(ap.parse_args())

        self.image = settings_dict["image"]
        self.output = settings_dict["output"]
        self.sampling_f = settings_dict["samplingf"]
        self.bench = settings_dict["bench"]
        self.line_color = settings_dict["linecolor"]

    def print(self):
        print("Running vectorization with parameters:")
        print(f"\tSampling_f:\t{self.sampling_f}")
        print(f"\tBench:\t{self.bench}")
        print(f"\tLine color:\t{self.line_color}")