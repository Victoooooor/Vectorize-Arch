# Evaluate the different methods on some metrics

import datetime
import json
import os
from pathlib import Path
import time

import cv2
import numpy as np

from main import HybridDriver
from plain_bns import PlainBNSDriver
from potrace_multiscan import PotraceMultiscanDriver
from util.settings import Settings
from util.vectorization_driver import VectorizationDriver


class EvaluationStats:
    
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.filename = Path(settings.output).name

        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.output_dir = f'./img/eval/{self.filename}-{timestamp}'
        os.makedirs(self.output_dir)

        # Read in the input image (e.g., to do MSE error)
        self.input_image = cv2.imread(self.settings.image)
        h, w, _ = self.input_image.shape
        
        # Get some basic information about the original image
        self.input_image_info = {
            'filesize': Path(self.settings.image).stat().st_size,
            'height': h,
            'width': w,
        }

        self.stats = {}

    def _mse_error(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Compute MSE of two images. Averages over all color channels.
        """
        return np.mean(np.square(img1 - img2))

    def run_test(self, driver: VectorizationDriver) -> None:
        # Get driver name
        driver_obj = driver(self.settings)

        driver_name = driver_obj.get_name()
        print(f'\n\n\n=====\nRunning test for {driver_name}...')
        
        # Change the output to the current output directory
        settings.output = f'{self.output_dir}/{driver_name}_{self.filename}'

        # Run the vectorization method, get elapsed time
        start_time = time.time()
        driver_obj.run()
        end_time = time.time()

        # Get generated file sizes (SVG and PNG)
        svg_output_path = Path(settings.output)
        png_output_path = svg_output_path.with_suffix('.png')

        svg_filesize = svg_output_path.stat().st_size
        png_filesize = png_output_path.stat().st_size

        # Compute MSE
        png_output = cv2.imread(png_output_path.as_posix())
        mse = self._mse_error(self.input_image, png_output)

        # Store statistics for this vectorization method
        self.stats[driver_name] = {
            'filename': settings.output,
            'elapsed': end_time-start_time,
            'svg_filesize': svg_filesize,
            'png_filesize': png_filesize,
            'mse': mse
        }

    def dump(self) -> None:
        stats_file = f'{self.output_dir}/stats.txt'

        # TODO:
        # - number of points (for triangulation methods)
        # - content loss

        with open(stats_file, 'w') as stats_fp:
            stats_fp.write('Settings:\n')
            self.settings.print(stats_fp)
            stats_fp.write('Input image info:\n')
            stats_fp.write(json.dumps(self.input_image_info, indent=4))
            stats_fp.write('Outputted files:\n')
            stats_fp.write(json.dumps(self.stats, indent=4))


if __name__ == '__main__':
    # TODO: possibly allow for multiple input files to test

    settings = Settings()
    settings.print()

    ev = EvaluationStats(settings)
    ev.run_test(PlainBNSDriver)
    ev.run_test(PotraceMultiscanDriver)
    ev.run_test(HybridDriver)

    ev.dump()