"""
Python class hierarchy that models retangle offsets, shapes and their rotations.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import copy
import bisect


@dataclass
class RectOff:
    """
    Class that models a rectangle offset: x/y position of size in x and y directions.
    """
    x: int
    y: int
    dx: int
    dy: int

    def __str__(self):
        return f'({self.x},{self.y})-({self.dx},{self.dy})'

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.dx == other.dx and self.dy == other.dy

    def __lt__(self, other):
        return (self.x, self.y, self.dx, self.dy) < (other.x, other.y, other.dx, other.dy)

    def __hash__(self):
        return hash((self.x, self.y, self.dx, self.dy))

    def clone(self):
        return copy.deepcopy(self)

    def rotate90(self, x_extent: int):
        """
        Rotate self by 90 degrees.
        """
        tx = self.x
        ty = self.y
        tdx = self.dx
        tdy = self.dy
        self.x = ty
        self.y = x_extent-(tx+tdx)
        self.dx = tdy
        self.dy = tdx

    def rotate180(self, x_extent: int, y_extent: int):
        """
        Rotate self by 180 degrees.
        """
        tx = self.x
        ty = self.y
        tdx = self.dx
        tdy = self.dy
        self.x = x_extent-(tx+tdx)
        self.y = y_extent-(ty+tdy)

    def rotate270(self, y_extent: int):
        """
        Rotate self by 270 degrees.
        """
        tx = self.x
        ty = self.y
        tdx = self.dx
        tdy = self.dy
        self.x = y_extent-(ty+tdy)
        self.y = tx
        self.dx = tdy
        self.dy = tdx


@dataclass
class Shape:
    """
    Class that models a shape represented by a list of rectangle offsets.
    The list is ordered and contains no duplicates.
    """
    x_extent: int
    y_extent: int
    rects: list[RectOff] = field(default_factory=list)

    def __str__(self):
        items = {str(r) for r in self.rects}
        return '{'+','.join(items)+'}'

    def __eq__(self, other):
        return self.x_extent == other.x_extent and self.y_extent == other.y_extent and self.rects == other.rects

    def __hash__(self):
        return hash((self.x_extent, self.y_extent, tuple(self.rects)))

    def clone(self) -> Shape:
        return copy.deepcopy(self)

    def add(self, rect: RectOff):
        """
        Add a rectangle offset to the shape.


        Args:
            rect: the rectangle offset
        """
        bisect.insort(self.rects, rect)

    def len(self) -> int:
        return len(self.rects)

    def is_square(self) -> bool:
        return self.len() == 1 and self.rects[0].dx == self.rects[0].dy

    def is_rectangle(self) -> bool:
        return self.len() == 1 and self.rects[0].dx != self.rects[0].dy

    def is_complex(self) -> bool:
        return self.len() > 1

    def rotate90(self):
        """
        Rotate self by 90 degrees.
        """
        for r in self.rects:
            r.rotate90(self.x_extent)
        self.rects.sort()

    def rotate180(self):
        """
        Rotate self by 180 degrees.
        """
        for r in self.rects:
            r.rotate180(self.x_extent, self.y_extent)
        self.rects.sort()

    def rotate270(self):
        """
        Rotate self by 270 degrees.
        """
        for r in self.rects:
            r.rotate270(self.y_extent)
        self.rects.sort()

    def orientations(self, unary: bool = False) -> ShapeOrientations:
        """
        Create all rotations of a shape, in 90 degree increments.
        """
        so = ShapeOrientations([self])
        if unary or self.is_square():
            return so
        r90 = self.clone()
        r90.rotate90()
        so.add(r90)
        if self.is_rectangle():
            return so
        r180 = self.clone()
        r180.rotate180()
        so.add(r180)
        r270 = self.clone()
        r270.rotate270()
        so.add(r270)
        return so


@dataclass
class ShapeOrientations:
    """
    Class that models multiple rotations of a shape.
    """
    shapes: list[Shape] = field(default_factory=list)

    def __str__(self):
        items = {str(r) for r in self.shapes}
        return '{'+','.join(items)+'}'

    def add(self, shape: Shape):
        """
        Add a shape to the list of orientations.
        """
        if shape not in self.shapes:
            self.shapes.append(shape)
