from typing import List, Tuple
import cairo

Pair = Tuple[int, int]
IMG_SIZE = 500


def draw_triangles(file_name: str, triangles: List[Tuple[Pair, Pair, Pair]]) -> None:
    with cairo.SVGSurface(file_name, IMG_SIZE, IMG_SIZE) as surface:
        ctx = cairo.Context(surface)
        ctx.set_line_width(1)
        for triangle in triangles:
            _draw_triangle(ctx, triangle)
        ctx.stroke()


def _draw_triangle(ctx: cairo.Context, triangle_points: Tuple[Pair, Pair, Pair]) -> None:
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


if __name__ == '__main__':
    file_name = 'example.svg'
    triangle_points = ((240, 40), (240, 160), (350, 160))
    draw_triangles(file_name, [triangle_points])
