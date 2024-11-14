from __future__ import annotations
from dataclasses import dataclass
from typing import List, TypeAlias, Literal, Iterable

import c

Cell: TypeAlias = c.ANSIColour
Row = List[Cell]
Face: TypeAlias = List[Row]

PRINT_DIRECTIONS: TypeAlias = Literal['horizontal', 'vertical']


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
    def from_ranges(order: List[c._RGB_COMPONENT]) -> RGBCube:
        ranges: dict[c._RGB_COMPONENT, range] = {
            'r': range(6),
            'g': range(6),
            'b': range(6),
        }

        faces = []
        for r0 in ranges[order[0]]:
            face = []
            for r1 in ranges[order[1]]:
                row = []
                for r2 in ranges[order[2]]:
                    cell = c.from_cube_coords(**{
                        order[0]: r0,
                        order[1]: r1,
                        order[2]: r2
                    })
                    row.append(cell)
                face.append(row)
            faces.append(face)

        return RGBCube(Faces(faces))


for i in range(16, 232):
    cell = c.from_ansi(i)
    print(f'{i:3d} {str(cell.rgb):>16s}', cell.colorise(' '*8))

RGBCube.from_ranges(['r', 'g', 'b']).print()
RGBCube.from_ranges(['b', 'g', 'r']).print()
