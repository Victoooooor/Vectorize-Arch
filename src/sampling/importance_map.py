import numpy as np
import cv2

from util.settings import Settings




class ImportanceMap:
    """
    First step of blue-noise sampling, based on Zhao et al.
    """

    def __init__(self):
        """
        Set up "improved" Sobel filters for blue-noise sampling.
        """
        k1 = np.array([
            [-1, -2, -1],
            [0, 0, 0],
            [1, 2, 1]])
        k2 = np.array([
            [-1, 0, 1],
            [-2, 0, 2],
            [-1, 0, 1]])
        k3 = np.array([
            [2, 1, 0],
            [1, 0, -1],
            [0, -1, -2]])
        k4 = np.array([
            [0, 1, 2],
            [-1, 0, 1],
            [-2, -1, 0]])
        self.filters = [k1, k2, k3, k4]

    def _get_importance(self, x: np.ndarray, gamma: float) -> np.ndarray:
        """
        Perform importance map pixel-wise over the image.
        """
        pix_max = np.amax(x)
        power = 1 / gamma
        importance = (x / pix_max) ** power
        return importance * 255

    def run(self, settings: Settings, img: np.ndarray, gamma: float = 0.1) -> np.ndarray:
        """
        Blue-noise sampling driver
        """

        # Apply each filter to the image
        filtered_images = [
            np.absolute(cv2.filter2D(img, -1, k)) 
            for k in self.filters
        ]

        # Get the pixel-wise max value
        image_max = np.maximum.reduce(filtered_images)

        # Return importance map
        return self._get_importance(image_max, gamma)

    def run_and_export(self, settings: Settings, img: np.ndarray) -> np.ndarray:
        """
        Same as run(), but also saves result to file.
        """
        importance_map = self.run(settings, img)
        cv2.imwrite(settings.output, importance_map)
        return importance_map