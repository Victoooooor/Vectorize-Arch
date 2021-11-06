import argparse
import cv2

import numpy as np
import matplotlib.pyplot as plt


def importance(x, gamma):
    pix_max = x.max()
    power = 1 / gamma
    imp = (x / pix_max) ** power
    return imp * 255


def minmax(v):
    if v > 255:
        v = 255
    if v < 0:
        v = 0
    return v


def dithering_color(inMat, samplingF):
    # https://en.wikipedia.org/wiki/Floyd–Steinberg_dithering
    # https://www.youtube.com/watch?v=0L2n8Tg2FwI&t=0s&list=WL&index=151
    # input is supposed as color
    # grab the image dimensions
    h = inMat.shape[0]
    w = inMat.shape[1]

    # Loop over the image
    for y in range(0, h - 1):
        for x in range(1, w - 1):
            # Threshold the pixel
            old_b = inMat[y, x, 0]
            old_g = inMat[y, x, 1]
            old_r = inMat[y, x, 2]

            new_b = np.round(samplingF * old_b / 255.0) * (255 / samplingF)
            new_g = np.round(samplingF * old_g / 255.0) * (255 / samplingF)
            new_r = np.round(samplingF * old_r / 255.0) * (255 / samplingF)

            inMat[y, x, 0] = new_b
            inMat[y, x, 1] = new_g
            inMat[y, x, 2] = new_r

            quant_error_b = old_b - new_b
            quant_error_g = old_g - new_g
            quant_error_r = old_r - new_r

            inMat[y, x + 1, 0] = minmax(inMat[y, x + 1, 0] + quant_error_b * 7 / 16.0)
            inMat[y, x + 1, 1] = minmax(inMat[y, x + 1, 1] + quant_error_g * 7 / 16.0)
            inMat[y, x + 1, 2] = minmax(inMat[y, x + 1, 2] + quant_error_r * 7 / 16.0)

            inMat[y + 1, x - 1, 0] = minmax(inMat[y + 1, x - 1, 0] + quant_error_b * 3 / 16.0)
            inMat[y + 1, x - 1, 1] = minmax(inMat[y + 1, x - 1, 1] + quant_error_g * 3 / 16.0)
            inMat[y + 1, x - 1, 2] = minmax(inMat[y + 1, x - 1, 2] + quant_error_r * 3 / 16.0)

            inMat[y + 1, x, 0] = minmax(inMat[y + 1, x, 0] + quant_error_b * 5 / 16.0)
            inMat[y + 1, x, 1] = minmax(inMat[y + 1, x, 1] + quant_error_g * 5 / 16.0)
            inMat[y + 1, x, 2] = minmax(inMat[y + 1, x, 2] + quant_error_r * 5 / 16.0)

            inMat[y + 1, x + 1, 0] = minmax(inMat[y + 1, x + 1, 0] + quant_error_b * 1 / 16.0)
            inMat[y + 1, x + 1, 1] = minmax(inMat[y + 1, x + 1, 1] + quant_error_g * 1 / 16.0)
            inMat[y + 1, x + 1, 2] = minmax(inMat[y + 1, x + 1, 2] + quant_error_r * 1 / 16.0)

            #   quant_error  := oldpixel - newpixel
            #   pixel[x + 1][y    ] := pixel[x + 1][y    ] + quant_error * 7 / 16
            #   pixel[x - 1][y + 1] := pixel[x - 1][y + 1] + quant_error * 3 / 16
            #   pixel[x    ][y + 1] := pixel[x    ][y + 1] + quant_error * 5 / 16
            #   pixel[x + 1][y + 1] := pixel[x + 1][y + 1] + quant_error * 1 / 16

    # Return the thresholded image
    return inMat


def rect_contains(rect, point):
    """Check if the provided point is inside the provided rectangle."""
    if point[0] < rect[0]:
        return False
    elif point[1] < rect[1]:
        return False
    elif point[0] > rect[2]:
        return False
    elif point[1] > rect[3]:
        return False
    return True


def draw_point(img, p, color):
    """# Draw a point."""
    cv2.circle(img, p, 2, color, cv2.cv.CV_FILLED, cv2.CV_AA, 0)


def draw_delaunay(img, subdiv, delaunay_color):
    """Draw delaunay triangles."""
    triangleList = subdiv.getTriangleList()
    size = img.shape
    r = (0, 0, size[1], size[0])

    for t in triangleList:
        pt1 = (int(t[0]), int(t[1]))
        pt2 = (int(t[2]), int(t[3]))
        pt3 = (int(t[4]), int(t[5]))

        if rect_contains(r, pt1) and rect_contains(r, pt2) and rect_contains(r, pt3):
            cv2.line(img, pt1, pt2, delaunay_color, 1, cv2.LINE_AA, 0)
            cv2.line(img, pt2, pt3, delaunay_color, 1, cv2.LINE_AA, 0)
            cv2.line(img, pt3, pt1, delaunay_color, 1, cv2.LINE_AA, 0)


if __name__ == '__main__':
    # Construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True, help="path to input image")
    args = vars(ap.parse_args())

    # Load the input image
    image = cv2.imread(args["image"])
    h, w, c = image.shape

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

    max_val = cv2.max(imfil_1, imfil_2)
    max_val = cv2.max(max_val, imfil_3)
    max_val = cv2.max(max_val, imfil_4)

    imp = importance(max_val, 0.01)
    # 0.5

    # saliency = cv2.saliency.StaticSaliencyFineGrained_create()
    # (success, saliencyMap) = saliency.computeSaliency(image)
    # cv2.imshow("cv2.saliency", saliencyMap)
    # cv2.imshow("Original", image)

    # cv2.imshow("Importance", imp)

    outMat_color = dithering_color(imp, 1)
    cv2.imshow('diffused', outMat_color)
    sampledpoint = (np.sum(outMat_color, axis=2) < 127) * 255

    points = []
    for i in range(h):
        for j in range(w):
            if sampledpoint[i][j] != 255:
                points.append((j, i))
    print(len(points))
    print(sampledpoint.shape)
    print(h, w)

    # cv2.imshow('points', sampledpoint)
    # (outMat_color > 0)*255
    # cv2.waitKey()

    rect = (0, 0, w, h)
    subdiv = cv2.Subdiv2D(rect)

    for x in points:
        subdiv.insert(x)

    triangle = subdiv.getTriangleList()

    draw_delaunay(outMat_color, subdiv, (255, 255, 255))

    cv2.imshow('triangle', outMat_color)
    plt.imshow(sampledpoint, cmap='gray')
    plt.show()
