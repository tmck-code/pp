from __future__ import annotations
from dataclasses import dataclass
from itertools import permutations
from typing import List, TypeAlias, Iterable, Literal, Iterator

import c

Cell: TypeAlias = c.ANSIColour
Row = List[Cell]


@dataclass
class Face:
    rows: List[Row]

    def rot90(self, face, n=1, flip=False):
        'Rotate a matrix 90 degrees, n times, optionally flipped'

        if flip:
            face = list(reversed(face))
        for _ in range(n):
            face = list(zip(*face[::-1]))
        return face

    def __iter__(self) -> Iterator[Row]:
        yield from self.rows

    def __next__(self) -> Row:
        return next(self.__iter__())


@dataclass
class Faces:
    faces: list[Face]

    def yield_rows(self) -> Iterable[Row]:
        for face in self.faces:
            for row in face:
                yield row

    def print(self) -> None:
        for row in self.yield_rows():
            print(*list(cell.colorise(f'{cell.ansi_n:^6}') for cell in row))


@dataclass
class RGBCube:
    faces: Faces

    def print(self):
        self.faces.print()

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
                    cell = c.from_cube_coords(**{
                        c1: r1, c2: r2, c3: r3
                    })
                    row.append(cell)
                face.append(row)
            faces.append(face)

        return RGBCube(Faces(faces))


for i in range(16, 232):
    cell = c.from_ansi(i)
    print(f'{i:3d} {str(cell.rgb):>16s}', cell.colorise(' '*8))


for c1, c2, c3 in permutations(('r', 'g', 'b')):
    print('-'*80, (c1, c2, c3), sep='\n')
    RGBCube.from_ranges(c1, c2, c3).print()
