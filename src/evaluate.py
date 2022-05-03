# Evaluate the different methods on some metrics

import datetime
import json
import os
from pathlib import Path
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

        # to be filled with the image paths
        self.png_paths = {}

    def run_test(self, driver: VectorizationDriver) -> None:
        # Get driver name
        driver_obj = driver(self.settings)

        driver_name = driver_obj.get_name()
        print(f'Running test for {driver_name}...')
        
        # Change the output to the current output directory
        settings.output = f'{self.output_dir}/{driver_name}_{self.filename}'
        self.png_paths[driver_name] = settings.output

        # Run the vectorization method
        driver_obj.run()

    def dump(self) -> None:
        stats_file = f'{self.output_dir}/stats.txt'

        with open(stats_file, 'w') as stats_fp:
            stats_fp.write('Outputted files:')
            stats_fp.write(json.dumps(self.png_paths))


if __name__ == '__main__':
    # TODO: possibly allow for multiple input files to test

    settings = Settings()
    settings.print()

    ev = EvaluationStats(settings)
    ev.run_test(HybridDriver)
    ev.run_test(PlainBNSDriver)
    ev.run_test(PotraceMultiscanDriver)

    ev.dump()