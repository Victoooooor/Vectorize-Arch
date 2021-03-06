import cairo

from util.geometry_types import Triangle, TriangleList


class SVGWriter():
    def __init__(self, w: int, h: int, line_width: int) -> None:
        """
        Keyword arguments:
            img_size -- the height and width dimension of the canvas (img_size by img_size)
            line_width -- the line width used for the vector graphics
        """
        self.img_size = (w, h)
        self.line_width = line_width

    def draw_triangles(self, filename: str, triangles: TriangleList) -> None:
        """Draw the provided list of triangles into an SVG file.

        Keyword arguments:
            filename -- the filename to save the triangles to
            triangles -- a list of tuples representing the triangles, where each coordinate is represented by a tuple of (x, y)
        """
        w, h = self.img_size
        with cairo.SVGSurface(filename, w, h) as surface:
            ctx = cairo.Context(surface)
            ctx.set_line_width(self.line_width)
            for triangle in triangles:
                self._draw_triangle(ctx, triangle)

    def _draw_triangle(self, ctx: cairo.Context, triangle_points: Triangle) -> None:
        """Draw a single triangle using the provided Context."""
        # Extract points
        x1, y1, x2, y2, x3, y3, r, g, b = triangle_points

        ctx.set_source_rgb(r/255., g/255., b/255.)

        # Draw triangle
        ctx.new_path()
        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)
        ctx.line_to(x3, y3)
        ctx.close_path()
        ctx.fill()


if __name__ == '__main__':
    img_size = 500
    line_width = 1
    converter = SVGWriter(img_size, img_size, line_width)

    filename = 'example.svg'
    triangles = [
        ((240, 40), (240, 160), (350, 160)),
        ((100, 20), (100, 50), (50, 50)),
    ]
    converter.draw_triangles(filename, triangles)
