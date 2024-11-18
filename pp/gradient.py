from __future__ import annotations
from itertools import repeat
from itertools import chain
from dataclasses import dataclass
from itertools import permutations
import os
import re
from typing import List, TypeAlias, Iterable, Literal, Iterator, Dict

from pp import c

Cell: TypeAlias = c.ANSIColour
Row = List[Cell]


@dataclass
class Face:
    rows: List[Row]

    def rot90(self, n: int = 1, flip: bool = False) -> Face:
        'Rotate a matrix 90 degrees, n times, optionally flipped'

        face = self.rows
        if flip:
            face = list(reversed(face))
        for _ in range(n):
            face = list(zip(*face[::-1]))
        return Face(face)

    def __iter__(self) -> Iterator[Row]:
        yield from self.rows

    def __next__(self) -> Row:
        return next(self.__iter__())

    def __getitem__(self, i: int) -> Row:
        return self.rows[i]

    @staticmethod
    def empty_face(width: int = 6) -> Face:
        return Face([c.from_ansi(16)] * width for _ in range(width))

    def iter_s(self, padding_top: int = 0, padding_bottom: int = 0) -> Iterable[str]:
        for row in self.__iter__():
            p = [cell.colorise(' '*6) for cell in row]
            r = [cell.colorise(f'{cell.ansi_n:^6}') for cell in row]

            for row in chain(repeat(p, padding_top), [r], repeat(p, padding_bottom)):
                yield ''.join(row)

    def print(self, padding_top: int = 0, padding_bottom: int = 0) -> None:
        'Print the face, with optional cell padding top/bottom to make it more "square"'

        for row in self.iter_s(padding_top, padding_bottom):
            print(row)

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

    def iter_s(self, padding_top: int = 0, padding_bottom: int = 0) -> Iterable[str]:
        for face_row in self.faces:
            for row in zip(*[face.iter_s(padding_top, padding_bottom) for face in face_row]):
                yield ''.join(row)

    def as_str(self, padding_top: int = 0, padding_bottom: int = 0) -> str:
        s = ''
        for row in self.iter_s(padding_top, padding_bottom):
            s += row + '\n'
        return s

    def print(self, padding_top: int = 0, padding_bottom: int = 0) -> None:
        'Print the faces of the cube, with optional cell padding top/bottom to make it more "square"'

        print(self.as_str(padding_top, padding_bottom))


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

    def find_face_with_edge(self, face: Face, edge_type: str='ts') -> Face:
        if edge_type == 'ts':    edge = face[0]
        elif edge_type == 'bs':  edge = face[-1]
        elif edge_type == 'lhs': edge = [r[0] for r in face]
        elif edge_type == 'rhs': edge = [r[-1] for r in face]

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

    def print(self, grid_sep: str = ' '*2) -> None:
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
                print(f'{name:<{c.str_width}s}',end=grid_sep)
            print()
            for rows in zip(*[c.faces.iter_s() for n,c in g.items()]):
                print(grid_sep.join(rows))


for i in range(16, 232):
    cell = c.from_ansi(i)
    print(f'{i:3d} {str(cell.rgb):>16s}', cell.colorise(' '*8))


print('\n'+'~'*80+'\n')

coll=RGBCubeCollection({
    'rgb': RGBCube.from_ranges('r', 'g', 'b'),
    'rbg': RGBCube.from_ranges('b', 'r', 'g'),
    'grb': RGBCube.from_ranges('g', 'r', 'b'),
})
coll.print()
