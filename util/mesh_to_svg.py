from typing import List, Tuple
import cairo

Pair = Tuple[int, int]


class SVGWriter():
    def __init__(self, img_size: int, line_width: int) -> None:
        self.img_size = img_size
        self.line_width = line_width


    def draw_triangles(self, file_name: str, triangles: List[Tuple[Pair, Pair, Pair]]) -> None:
        with cairo.SVGSurface(file_name, self.img_size, self.img_size) as surface:
            ctx = cairo.Context(surface)
            ctx.set_line_width(self.line_width)
            for triangle in triangles:
                self._draw_triangle(ctx, triangle)


    def _draw_triangle(self, ctx: cairo.Context, triangle_points: Tuple[Pair, Pair, Pair]) -> None:
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

    file_name = 'example.svg'
    triangles = [
        ((240, 40), (240, 160), (350, 160)),
        ((100, 20), (100, 50), (50, 50)),
    ]
    converter.draw_triangles(file_name, triangles)
