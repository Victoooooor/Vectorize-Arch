from util.settings import Settings
from pathlib import Path
import cairosvg


class PNGWriter:
    """
    Convert SVG to PNG (for comparison purposes)
    """

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    def run(self, settings: Settings) -> None:
        # Change path to .png extension
        # https://stackoverflow.com/a/47528275
        path = Path(settings.output)
        png_path = path.with_suffix('.png').as_posix()

        # https://cairosvg.org/documentation/
        cairosvg.svg2png(
            url=settings.output, 
            write_to=png_path,
            output_width=self.width,
            output_height=self.height)
