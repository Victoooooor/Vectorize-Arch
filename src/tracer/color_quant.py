from typing import Tuple
import numpy as np
import cv2
import subprocess as sp
import xml.etree.ElementTree as ET
from time import sleep

from util.settings import Settings


class ColorQuantization:
    """
    Color quantization using k-means clustering.

    Based on https://www.analyticsvidhya.com/blog/2021/07/colour-quantization-using-k-means-clustering-and-opencv/
    """

    def run(self, settings: Settings, img: np.ndarray, k: int, stacked: bool = False) -> Tuple[np.ndarray, np.ndarray]:
        img_flat = np.float32(img).reshape(-1, 3)
        condition = (cv2.TERM_CRITERIA_EPS +
                     cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, center = cv2.kmeans(
            img_flat, k, None, condition, 10, cv2.KMEANS_RANDOM_CENTERS)
        # center = np.uint8(center)
        # img_out = center[label.flatten()]
        # img_out = img_out.reshape(img.shape)
        # return img_out

        h, w, _ = img.shape
        labels = labels.reshape(h, w)
        color_scans = np.zeros((k, h, w), dtype=np.uint8)

        if stacked:
            for i in range(k):
                color_scans[i] = labels >= i
        else:
            for i in range(k):
                color_scans[i] = labels == i

        return (1-color_scans) * 255, center

    def _rgb_to_hex(self, rgb: np.ndarray) -> str:
        b, g, r = rgb.astype(np.uint8)
        # https://stackoverflow.com/a/12638477
        return f'#{r:0{2}x}{g:0{2}x}{b:0{2}x}'

    def run_and_export(self, settings: Settings, img: np.ndarray, k: int, stacked: bool = False) -> np.ndarray:
        img_scans, center = self.run(settings, img, k, stacked)

        # Export images separately
        for i in range(k):
            filename = f"img/out{i}"
            cv2.imwrite(f"{filename}.bmp", img_scans[i, :, :])

            # We use --fillcolor to get rid of the alpha (transparency) dimension
            extraargs = f'--color {self._rgb_to_hex(center[i, :])}' if stacked else '--fillcolor #ffffff'
            sp.Popen(
                f"potrace {filename}.bmp -o {filename}.svg -b svg {extraargs}".split(' '))

        # Join together into a single image if stacked
        if stacked:
            sleep(1) # make sure potrace files are generated
            tree = ET.parse('img/out0.svg')
            root = tree.getroot()

            for i in range(1, k):
                filename = f'img/out{i}.svg'
                tree2 = ET.parse(filename)
                root2 = tree2.getroot()

                # Append all children of other SVGs into root
                # of first SVG
                for child in root2:
                    root.append(child)

            tree.write(settings.output)

        return img
