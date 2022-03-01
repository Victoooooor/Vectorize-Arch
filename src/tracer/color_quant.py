import numpy as np
import cv2
import subprocess as sp

from util.settings import Settings


class ColorQuantization:
    """
    Color quantization using k-means clustering.

    Based on https://www.analyticsvidhya.com/blog/2021/07/colour-quantization-using-k-means-clustering-and-opencv/
    """

    def run(self, settings: Settings, img: np.ndarray, k: int) -> np.ndarray:
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
        for i in range(k):
            color_scans[i] = labels == i

        return color_scans * 255

    def run_and_export(self, settings: Settings, img: np.ndarray, k: int) -> np.ndarray:
        img_scans = self.run(settings, img, k)

        for i in range(k):
            filename = f"img/out{i}"
            cv2.imwrite(f"{filename}.bmp", img_scans[i, :, :])
            sp.Popen(
                f"potrace {filename}.bmp -o {filename}.svg -b svg".split(' '))

        return img
