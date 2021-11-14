from typing import Tuple

import time
import argparse
import cv2

import numpy as np
import matplotlib.pyplot as plt


def importance(x: np.ndarray, gamma: float) -> np.ndarray:
    pix_max = x.max()
    power = 1 / gamma
    imp = (x / pix_max) ** power
    return imp * 255


def threshold_pixel(pixel: int) -> int:
    """Threshold a pixel value to be in the range [0, 255]."""
    if pixel > 255:
        pixel = 255
    elif pixel < 0:
        pixel = 0
    return pixel


def dither_image(image: np.ndarray, sampling_f: float) -> np.ndarray:
    """Perform Floyd-Steinberg dithering.
    Based on:
    https://en.wikipedia.org/wiki/Floyd–Steinberg_dithering
    https://www.youtube.com/watch?v=0L2n8Tg2FwI&t=0s&list=WL&index=151

    Keyword arguments:
        image -- a matrix representing an RGB single image
        sampling_f -- 
    """
    # Get the image dimensions
    h = image.shape[0]
    w = image.shape[1]

    # Loop over the image
    for y in range(0, h - 1):
        for x in range(1, w - 1):
            for channel in range(0, 3):
                # Update the current pixel
                old_pixel = image[y, x, channel]
                new_pixel = np.round(sampling_f * old_pixel / 255.0) * (255 / sampling_f)
                image[y, x, channel] = new_pixel
                quant_error = old_pixel - new_pixel

                # Perform error diffusion
                image[y, x + 1, channel] = threshold_pixel(image[y, x + 1, channel] + quant_error * 7 / 16.0)
                image[y + 1, x - 1, channel] = threshold_pixel(image[y + 1, x - 1, channel] + quant_error * 3 / 16.0)
                image[y + 1, x, channel] = threshold_pixel(image[y + 1, x, channel] + quant_error * 5 / 16.0)
                image[y + 1, x + 1, channel] = threshold_pixel(image[y + 1, x + 1, channel] + quant_error * 1 / 16.0)

    return image


def rect_contains(rect: Tuple[int, int, int, int], point: Tuple[int, int]) -> bool:
    """Check if the provided point is inside the provided rectangle."""
    if point[0] < rect[0] or point[0] > rect[2]:
        return False
    elif point[1] < rect[1] or point[1] > rect[3]:
        return False
    return True


def draw_delaunay(image: np.ndarray, subdiv: cv2.Subdiv2D, color: Tuple[int, int, int]) -> None:
    """Draw delaunay triangles.

    Keyword arguments:
        image --
        subdiv --
        color -- a tuple representing the RGB values of the desired color
    """
    triangle_list = subdiv.getTriangleList()
    size = image.shape
    r = (0, 0, size[1], size[0])

    for t in triangle_list:
        pt1 = (int(t[0]), int(t[1]))
        pt2 = (int(t[2]), int(t[3]))
        pt3 = (int(t[4]), int(t[5]))

        if rect_contains(r, pt1) and rect_contains(r, pt2) and rect_contains(r, pt3):
            cv2.line(image, pt1, pt2, color, 1, cv2.LINE_AA, 0)
            cv2.line(image, pt2, pt3, color, 1, cv2.LINE_AA, 0)
            cv2.line(image, pt3, pt1, color, 1, cv2.LINE_AA, 0)


if __name__ == '__main__':
    # Measure running time
    start_time = time.time()

    # Construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True, help="path to input image")
    args = vars(ap.parse_args())

    # Load the input image
    image = cv2.imread(args["image"])
    h, w, c = image.shape

    # 'Improved' Sobel filters
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

    imfil_1 = np.absolute(cv2.filter2D(image, -1, k1))
    imfil_2 = np.absolute(cv2.filter2D(image, -1, k2))
    imfil_3 = np.absolute(cv2.filter2D(image, -1, k3))
    imfil_4 = np.absolute(cv2.filter2D(image, -1, k4))

    # Get the pixel-wise max value
    image_max = cv2.max(imfil_1, imfil_2)
    image_max = cv2.max(image_max, imfil_3)
    image_max = cv2.max(image_max, imfil_4)

    imp = importance(image_max, 0.01)
    # 0.5

    # saliency = cv2.saliency.StaticSaliencyFineGrained_create()
    # (success, saliencyMap) = saliency.computeSaliency(image)
    # cv2.imshow("cv2.saliency", saliencyMap)
    # cv2.imshow("Original", image)

    # cv2.imshow("Importance", imp)

    outMat_color = dither_image(imp, 1)
    cv2.imshow('diffused', outMat_color)
    sampled_point = (np.sum(outMat_color, axis=2) < 127) * 255

    points = []
    for i in range(h):
        for j in range(w):
            if sampled_point[i][j] != 255:
                points.append((j, i))
    print(len(points))
    print(sampled_point.shape)
    print(h, w)

    # cv2.imshow('points', sampledpoint)
    # (outMat_color > 0)*255
    # cv2.waitKey()

    rect = (0, 0, w, h)
    subdiv = cv2.Subdiv2D(rect)

    for x in points:
        subdiv.insert(x)

    draw_delaunay(outMat_color, subdiv, (255, 255, 255))

    # Display running time
    end_time = time.time()
    print("Time taken:", end_time-start_time)

    cv2.imshow('triangle', outMat_color)
    plt.imshow(sampled_point, cmap='gray')
    plt.show()
