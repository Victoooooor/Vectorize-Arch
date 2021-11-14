from typing import List, Tuple
import cairo

Pair = Tuple[int, int]


class SVGWriter():
    def __init__(self, img_size: int, line_width: int) -> None:
        """
        Keyword arguments:
            img_size -- the height and width dimension of the canvas (img_size by img_size)
            line_width -- the line width used for the vector graphics
        """
        self.img_size = img_size
        self.line_width = line_width

    def draw_triangles(self, filename: str, triangles: List[Tuple[Pair, Pair, Pair]]) -> None:
        """Draw the provided list of triangles into an SVG file.

        Keyword arguments:
            filename -- the filename to save the triangles to
            triangles -- a list of tuples representing the triangles, where each coordinate is represented by a tuple of (x, y)
        """
        with cairo.SVGSurface(filename, self.img_size, self.img_size) as surface:
            ctx = cairo.Context(surface)
            ctx.set_line_width(self.line_width)
            for triangle in triangles:
                self._draw_triangle(ctx, triangle)

    def _draw_triangle(self, ctx: cairo.Context, triangle_points: Tuple[Pair, Pair, Pair]) -> None:
        """Draw a single triangle using the provided Context."""
        # Extract points
        point1, point2, point3 = triangle_points
        x1, y1 = point1
        x2, y2 = point2
        x3, y3 = point3

        # Draw triangle
        ctx.new_path()
        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)
        ctx.line_to(x3, y3)
        ctx.close_path()
        ctx.stroke()


if __name__ == '__main__':
    img_size = 500
    line_width = 1
    converter = SVGWriter(img_size, line_width)

    filename = 'example.svg'
    triangles = [
        ((240, 40), (240, 160), (350, 160)),
        ((100, 20), (100, 50), (50, 50)),
    ]
    converter.draw_triangles(filename, triangles)
