# Run potrace scans with color quantization


import cv2
from tracer.color_quant import ColorQuantization
from util.settings import Settings
from util.svg_to_png import PNGWriter


if __name__ == '__main__':
    settings = Settings()
    settings.print()

    # Load the input image
    print("Loading image...")
    image = cv2.imread(settings.image)

    h, w, _ = image.shape

    # Color quantization
    k = 4
    print(f"Color quantization with k={k}")
    cq = ColorQuantization()
    cq.run_and_export(settings, image, k, stacked=True)

    # Also export to PNG
    pw = PNGWriter(w, h)
    pw.run(settings)