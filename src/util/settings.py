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
        ap.add_argument("-ic", "--importance",
            required=False, const=100.0, type=float, nargs='?', default=100.0,
            help="importance map scaling coefficient")
        ap.add_argument("-d", "--decimation",
            required=False, const=10, type=int, nargs='?', default=10,
            help="decimation factor")
        ap.add_argument("-ps", "--potscans",
            required=False, const=4, type=int, nargs='?', default=4,
            help="number of potrace scans")
        ap.add_argument("-uad", "--unifierattdist",
            required=False, const=15, type=int, nargs='?', default=15,
            help="unifier attraction distance")
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
        self.importance_coef = settings_dict["importance"]
        self.decimation_coef = settings_dict["decimation"]
        self.potrace_scans = settings_dict["potscans"]
        self.unifier_attraction_distance = settings_dict["unifierattdist"]

    def print(self, fp=None):
        pr = print if fp is None else lambda m: fp.write(m + '\n')

        pr("Running vectorization with parameters:")
        pr(f"\tInput file:\t{self.image}")
        pr(f"\tSampling_f:\t{self.sampling_f}")
        pr(f"\tBench:\t{self.bench}")
        pr(f"\tLine color:\t{self.line_color}")
        pr(f"\tImportance map coef:\t{self.importance_coef}")
        pr(f"\tDecimation coef:\t{self.decimation_coef}")
        pr(f"\tPotrace scans:\t{self.potrace_scans}")
        pr(f"\tUnfifier attraction distance:\t{self.unifier_attraction_distance}")