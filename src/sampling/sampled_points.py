from typing import Optional, Tuple, List
from math import ceil

# Generic type for point coordinates. Can easily change
# between `float`s and `int`s if necessary.
# (Calling the generic type `t` is a OCaml thing)
t = float

# Coordinate pair (x, y)
coord = Tuple[t, t]


class SampledPoint:
    """
    Represents a single sampled point. May include information
    useful for image simplification (e.g., nearest curve, etc.).
    """

    def __init__(self, xy: coord) -> None:
        self.xy = xy

        # TODO: add other fields as necessary

    def to_coord(self) -> coord:
        return self.xy


class SampledPoints:
    """
    Represents the set of sampled points in the image, along with
    a faster lookup method by quantizing the image to a 2-D grid,
    where each tile is of size (`tile_size` x `tile_size`).

    All points are assumed to be unique.
    """
    _tile = List[SampledPoint]

    def __init__(self,
                 width: int,
                 height: int,
                 tile_size: int,
                 coords: List[coord]) -> None:
        """
        Set up the map with the correct dimensions.
        """
        # Backing-store: a 2-D map (indexed by (tile_y, tile_x)),
        # where each tile represents a rectangular area of
        # `tile_size`^2.
        self.count = len(coords)    # for diagnostics only
        self.tile_size = tile_size
        self.x_divisions = int(ceil(width / tile_size))
        self.y_divisions = int(ceil(height / tile_size))
        self.bs: List[List[self._tile]] = [
            [[] for _ in range(self.x_divisions)]
            for _ in range(self.y_divisions)
        ]

        # Fill backing store
        for xy in coords:
            self._get_block(xy).append(SampledPoint(xy))

    def _get_block(self, xy: coord) -> _tile:
        """
        Returns the tile for a given coordinate.
        """
        x, y = xy
        return self.bs[int(y) // self.tile_size][int(x) // self.tile_size]

    def lookup(self, xy: coord) -> Optional[SampledPoint]:
        """
        Fast point lookup.

        Note: does not check that `xy` is within bounds.
        """
        for point in self._get_block(xy):
            if point.xy == xy:
                return point
        return None

    def update(self, xy_from: coord, xy_to: coord) -> None:
        """
        Update a point's location in the map.

        If point does not exist, silently fails. (Should this behavior
        be changed?)

        Don't need to use this function if all changes are
        made after all lookups.

        Note: does not (currently) change any information about the
        points other than their coordinates.

        Note: does not check that `xy_from` and `xy_to` are
        within bounds.
        """
        # Find point
        point = self.lookup(xy_from)
        if point is not None:
            # Remove point from old tile
            self._get_block(xy_from).remove(point)

            # Update point and re-insert
            point.xy = xy_to
            self._get_block(xy_to).append(point)

    def to_coords(self) -> List[coord]:
        """
        Export the point list back to a list of coordinates.
        """
        return [
            point.to_coord()
            for tile_y in range(self.y_divisions)
            for tile_x in range(self.x_divisions)
            for point in self.bs[tile_y][tile_x]
        ]

    def to_hist(self) -> None:
        """
        Used to visualize the distribution of points to see if
        this class is actually helpful.

        Just for diagnostic purposes.
        """
        import matplotlib.pyplot as plt

        # Get max bin size ("tile population")
        tile_populations = [
            len(self.bs[tile_y][tile_x])
            for tile_y in range(self.y_divisions)
            for tile_x in range(self.x_divisions)
        ]

        print(f"""SampledPoints:
            Number of points: {self.count}
            Tiles in x-direction: {self.x_divisions}
            Tiles in y-direction: {self.y_divisions}
            Expected points/tile: {self.count/self.x_divisions/self.y_divisions}
            Maximum tile population: {max(tile_populations)}
        """)

        plt.hist(tile_populations, 25)
        plt.title("Tile populations")
        plt.xlabel("Number of sampled points in tile")
        plt.xlabel("Frequency (# tiles)")
        plt.show()
