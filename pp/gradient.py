from __future__ import annotations
from itertools import repeat
from itertools import chain
from dataclasses import dataclass, field
from itertools import starmap
from functools import partial
import operator
import os
import re
from typing import List, TypeAlias, Iterable, Literal, Iterator, Dict

from pp import c

Cell: TypeAlias = c.ANSIColour
Row = List[Cell]


@dataclass
class Face:
    rows: List[Row]
    with_rotations: bool = True
    rotations: List[Face] = field(default_factory=list)
    flipped_rotations: List[Face] = field(default_factory=list)

    def __post_init__(self):
        if self.with_rotations:
            self.rotations = [Face._rot90(
                self.rows, n, flip=False) for n in range(4)]
            self.flipped_rotations = [Face._rot90(
                self.rows, n, flip=True) for n in range(4)]

    @staticmethod
    def _rot90(rows: List[Row], n: int = 1, flip: bool = False) -> Face:
        'Rotate a matrix 90 degrees, n times, optionally flipped'
        if flip:
            rows = list(reversed(rows))
        for _ in range(n):
            rows = list(zip(*rows[::-1]))
        return Face(rows, with_rotations=False)

    def rot90(self, n: int = 1, flip: bool = False) -> Face:
        'Rotate a matrix 90 degrees, n times, optionally flipped'
        if flip:
            return self.flipped_rotations[n]
        return self.rotations[n]

    def __iter__(self) -> Iterator[Row]:
        yield from self.rows

    def __next__(self) -> Row:
        return next(self.__iter__())

    def __getitem__(self, i: int) -> Row:
        return self.rows[i]

    @staticmethod
    def empty_face(width: int = 6) -> Face:
        return Face([[c.from_ansi(256)] * width] * width)

    def iter_s(self, padding_top: int = 0, padding_bottom: int = 0, cell_width: int = 15) -> Iterable[str]:
        for row in self.__iter__():
            p = [cell.colorise(' '*cell_width) for cell in row]
            # r = [cell.colorise(f'{cell.ansi_n:^{cell_width}}') for cell in row]
            r = [cell.colorise(f'{str(cell.rgb):^{cell_width}}')
                 for cell in row]

            for row in chain(repeat(p, padding_top), [r], repeat(p, padding_bottom)):
                yield ''.join(row)

    def print(self, padding_top: int = 0, padding_bottom: int = 0, cell_width: int = 6) -> None:
        'Print the face, with optional cell padding top/bottom to make it more "square"'

        print('\n'.join(self.iter_s(padding_top, padding_bottom, cell_width)))


ANSI_COLOURS = re.compile(r"""
    \x1b     # literal ESC
    \[       # literal [
    [;\d]*   # zero or more digits or semicolons
    [A-Za-z] # a letter
    """, re.VERBOSE)


@dataclass
class Faces:
    faces: list[list[Face]]

    def __iter__(self) -> Iterator[Face]:
        for face_row in self.faces:
            for face in face_row:
                yield face

    def __next__(self) -> Face:
        return next(self.__iter__())

    def iter_rows(self) -> Iterable[Row]:
        for face_row in self.faces:
            for row in zip(*face_row):
                yield row

    def iter_s(self, padding_top: int = 0, padding_bottom: int = 0, cell_width: int = 6) -> Iterable[str]:
        for face_row in self.faces:
            for row in zip(*[face.iter_s(padding_top, padding_bottom, cell_width) for face in face_row]):
                yield ''.join(row)

    def as_str(self, padding_top: int = 0, padding_bottom: int = 0, cell_width: int = 6) -> str:
        s = ''
        for row in self.iter_s(padding_top, padding_bottom, cell_width):
            s += row + '\n'
        return s

    def print(self, padding_top: int = 0, padding_bottom: int = 0, cell_width: int = 6) -> None:
        'Print the faces of the cube, with optional cell padding top/bottom to make it more "square"'

        print(self.as_str(padding_top, padding_bottom, cell_width))


def distance(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> float:
    return abs(sum(starmap(operator.sub, zip(c2, c1))))

# In[69]: c1, c2 = (95, 135, 0), (0, 135, 255)
# r = interp_xyz(c1, c2, 20)


def lerp(v0: float, v1: float, t: int) -> float:
    '''
    Precise method for iterpolation, which guarantees v = v1 when t = 1.
    This method is monotonic only when v0 * v1 < 0.
    Lerping between same values might not produce the same value
    (from: https://en.wikipedia.org/wiki/Linear_interpolation#Programming_language_support)
    '''
    return round((1 - (t/10)) * v0 + (t/10) * v1, 2)


def interp(v0: float, v1: float, n_t: int) -> list[float]:
    i = partial(lerp, v0, v1)
    ts = list(map(lambda x: x/((n_t-1)/10), range(0, n_t)))
    return list(map(i, ts))


def interp_xyz(c1: tuple[int, int, int], c2: tuple[int, int, int], n_t: int) -> list[float]:
    return list(zip(*starmap(interp, zip(c1, c2, repeat(n_t)))))


@dataclass
class RGBCube:
    faces: Faces
    width: int = 6

    def print(self) -> None:
        self.faces.print()

    @property
    def str_width(self) -> int:
        return max(len(ANSI_COLOURS.sub('', line)) for line in self.faces.iter_s())

    @staticmethod
    def compare_rows(r1: Row, r2: Row) -> bool:
        return all(c1 == c2 for c1, c2 in zip(r1, r2))

    def find_face_with_edge(self, face: Face, edge_type: str = 'ts') -> Face:
        if edge_type == 'ts':
            edge = face[0]
        elif edge_type == 'bs':
            edge = face[-1]
        elif edge_type == 'lhs':
            edge = [r[0] for r in face]
        elif edge_type == 'rhs':
            edge = [r[-1] for r in face]

        for face in self.faces:
            for rot in range(4):
                for flip in (False, True):
                    if edge_type == 'ts' and RGBCube.compare_rows(face.rot90(rot, flip=flip)[-1], edge):
                        return face.rot90(rot, flip=flip)
                    elif edge_type == 'bs' and RGBCube.compare_rows(face.rot90(rot, flip=flip)[0], edge):
                        return face.rot90(rot, flip=flip)
                    elif edge_type == 'lhs' and RGBCube.compare_rows([r[-1] for r in face.rot90(rot, flip=flip)], edge):
                        return face.rot90(rot, flip=flip)
                    elif edge_type == 'rhs' and RGBCube.compare_rows([r[0] for r in face.rot90(rot, flip=flip)], edge):
                        return face.rot90(rot, flip=flip)

    @staticmethod
    def from_ranges(c1: Literal[c._RGB_COMPONENT], c2: c._RGB_COMPONENT, c3: c._RGB_COMPONENT) -> RGBCube:
        '''
        Create a 6x6x6 cube of RGB values, where each face is a 6x6 grid of cells.
        Takes an 'order' of RGB components, where
        - c1 is iterated once per face
        - c2 is iterated once per row
        - c3 is iterated once per cell
        '''
        faces = []
        for r1 in range(6):
            face = []
            for r2 in range(6):
                row = []
                for r3 in range(6):
                    row.append(
                        c.from_cube_coords(**{c1: r1, c2: r2, c3: r3})
                    )
                face.append(row)
            faces.append([Face(face)])
        return RGBCube(Faces(faces))


@dataclass
class RGBCubeCollection:
    cubes: Dict[str, RGBCube]

    def __post_init__(self):
        self.width = os.get_terminal_size().columns

    def print(self, grid_sep: str = ' '*2, padding_top: int = 0, padding_bottom: int = 0, cell_width: int = 6) -> None:
        groups, current_group, current_width = [], {}, 0
        for name, cube in self.cubes.items():
            if sum(c.str_width for c in current_group.values()) + cube.str_width <= self.width:
                current_group[name] = cube
            else:
                groups.append(current_group)
                current_group = {name: cube}
        groups.append(current_group)

        for g in groups:
            for name, c in g.items():
                print(f'{name:<{c.str_width}s}', end=grid_sep)
            print()
            for rows in zip(*[c.faces.iter_s(padding_top, padding_bottom, cell_width) for n, c in g.items()]):
                print(grid_sep.join(rows))
