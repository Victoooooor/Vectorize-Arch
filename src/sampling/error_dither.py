from typing import List, Tuple
import numpy as np
import cv2

from util.settings import Settings


class ErrorDither:
    """
    Returns a set of points generated from error dithering, which is the second
    step in blue-noise sampling (performing the "sampling" step).

    Performs Floyd-Steinberg dithering, which is a form of error diffusion.

    The resulting shape is of the form Nx2, where N is the number of sampled points.

    Based on:
    - https://en.wikipedia.org/wiki/Floyd–Steinberg_dithering
    - https://www.youtube.com/watch?v=0L2n8Tg2FwI&t=0s&list=WL&index=151
    """

    def _threshold_pixel(self, pixel: int) -> int:
        """Threshold a pixel value to be in the range [0, 255]."""
        if pixel > 255:
            pixel = 255
        elif pixel < 0:
            pixel = 0
        return pixel

    def _dither(self, settings: Settings, img: np.ndarray) -> np.ndarray:
        # Get the image dimensions
        h = img.shape[0]
        w = img.shape[1]

        # Loop over the image
        for y in range(0, h - 1):
            for x in range(1, w - 1):
                for channel in range(3):
                    # Update the current pixel
                    old_pixel = img[y, x, channel]
                    new_pixel = np.round(
                        settings.sampling_f * old_pixel / 255.0) * (255 / settings.sampling_f)
                    img[y, x, channel] = new_pixel
                    quant_error = old_pixel - new_pixel

                    # Perform error diffusion
                    img[y, x + 1, channel] = self._threshold_pixel(
                        img[y, x + 1, channel] + quant_error * 7 / 16.0)
                    img[y + 1, x - 1, channel] = self._threshold_pixel(
                        img[y + 1, x - 1, channel] + quant_error * 3 / 16.0)
                    img[y + 1, x, channel] = self._threshold_pixel(
                        img[y + 1, x, channel] + quant_error * 5 / 16.0)
                    img[y + 1, x + 1, channel] = self._threshold_pixel(
                        img[y + 1, x + 1, channel] + quant_error * 1 / 16.0)

        return img

    def _threshold_sample(self, img: np.ndarray) -> List[Tuple[int, int]]:
        # Refactor to use argwhere
        # Why????
        sampled_point = (np.sum(img, axis=2) < 127) * 255

        h, w = sampled_point.shape
        points = []
        for i in range(h):
            for j in range(w):
                if sampled_point[i][j] != 255:
                    points.append((j, i))

        return points

    def run(self, settings: Settings, img: np.ndarray) -> List[Tuple[int, int]]:
        """
        Driver for the dithering process.
        """
        # dithering is not working correctly
        # img = self._dither(settings, img)
        sampled_points = self._threshold_sample(img)

        return sampled_points

    def run_and_export(self, settings: Settings, img: np.ndarray) -> List[Tuple[int, int]]:
        """
        Same as run(), but exports the sampled points to an image.
        """
        sampled = self.run(settings, img)

        # Plot sampled points
        h = img.shape[0]
        w = img.shape[1]
        img = np.zeros((h, w, 3), np.uint8)
        for (j, i) in sampled:
            img[i][j] = 255
        cv2.imwrite(settings.output, img)

        return sampled
