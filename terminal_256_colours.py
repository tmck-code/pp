#!/usr/bin/env python3

import re
import functools
import itertools
import operator

RESET = '\x1b[0m'

p = functools.partial(operator.is_, None)


def batched(items, n):
    for group in itertools.zip_longest(*[iter(items)] * n):
        yield list(itertools.filterfalse(p, group))


def colour_s(code, s): return f'\x1b[{code}m{s}'
def colour_fg(s, n): return colour_s(f'38;5;{n}', s)
def colour_bg(s, n): return colour_s(f'48;5;{n}', s)


def colour_cell(n):
    return colour_bg(f'{n:-3d}   ', n)


def empty_colour_cell(n):
    return colour_bg(' '*len(f'{n:-3d}')+' '*3, n)


def print_cell(n):
    print(colour_bg(f'{n:-3d}   ', n), RESET, end='', sep='')


def print_grid(grid):
    for row in grid:
        for cell in row:
            print_cell(cell)
        print()


def string_grid(grid, pad_top=1, pad_bottom=1):
    def _string_grid(grid):
        for row in grid:
            for i in range(pad_top):
                yield ''.join(empty_colour_cell(cell) for cell in row)+RESET
            yield ''.join(colour_cell(cell) for cell in row)+RESET
            for i in range(pad_bottom):
                yield ''.join(empty_colour_cell(cell) for cell in row)+RESET
    return '\n'.join(list(_string_grid(grid)))


ansi_colours = re.compile(r"""
    \x1b     # literal ESC
    \[       # literal [
    [;\d]*   # zero or more digits or semicolons
    [A-Za-z] # a letter
    """, re.VERBOSE)


def print_side_by_side(*grids):
    lengths = [max(len(ansi_colours.sub('', l))
                   for l in g.split('\n')) for g in grids]
    for lines in itertools.zip_longest(*[g.split('\n') for g in grids]):
        for length, chunk in zip(lengths, lines):
            if chunk is None or len(chunk) == 0:
                print(' '*length, end=' ')
            else:
                l = len(ansi_colours.sub('', chunk))
                print(chunk+' '*(length-l), end=' ')
        print()


def test1():
    return list(batched(range(16, 232), 12))


def test2():
    g = list(batched(range(16, 232), 12))
    for i in range(3):
        yield from itertools.islice(g, i, 36, 3)


def test3():
    g = list(batched(range(16, 232), 12))
    for i in range(6):
        row = list(itertools.islice(g, i, 36, 6))
        if i % 2 != 0:
            row = reversed(row)
        yield from row


def test4():
    g = list(batched(range(16, 232), 12))
    for i in range(6):
        yield from itertools.islice(g, i, 36, 6)


def test5():
    g = list(batched(range(16, 232), 6))
    for i in range(6):
        yield from itertools.islice(g, i, 36, 6)


def test6():
    g = list(batched(range(16, 232), 6))
    for i in range(6):
        row = list(itertools.islice(g, i, 36, 6))
        if i % 2 != 0:
            row = reversed(row)
        yield from row


def join_faces(faces):
    return list(itertools.chain(*faces))

def reverse(face):
    return list(reversed(face))


def rot90(face, n=1, flip=False):
    if flip:
        face = reverse(face)
    for _ in range(n):
        face = list(zip(*face[::-1]))
    return face


def print_cube(faces):
    empty_face = [[' '*6 for _ in range(6)] for _ in range(6)]

    for i, f in enumerate(faces):
        for row in f:
            print(''.join(row)+RESET)
        for row in list(reversed(faces[i+1])):
            print(''.join(row)+RESET)
        print('-'*80)
        if i+1 == len(faces)-1:
            break

    flattened = [
        (empty_face, faces[0], empty_face),
        (rot90(faces[1], 2), rot90(faces[2], 2), faces[3]),
        (empty_face, faces[4], empty_face),
        (empty_face, faces[5], empty_face),
    ]
    for faces in flattened:
        for row in zip(*faces):
            print(''.join(list(itertools.chain(*row)))+RESET)


def test7():
    faces = []
    g = list(batched(
        [colour_bg(f'{n:-3d}   ', n)+RESET for n in range(16, 232)],
        6
    ))
    for i in range(6):
        row = list(itertools.islice(g, i, 36, 6))
        # if i % 2 != 0:
        #     row = list(reversed(row))
        faces.append(row)

    print_cube(faces)


def rgb_cell(r, g, b, pad=False):
    s = f'{16 + 36*r:3d},{6*g:2d},{b:d}'
    if pad:
        s = ' '*len(s)
    return colour_bg(s=s, n=(16 + (36*r + 6*g + b)))+RESET


def rgb_to_ansi(r, g, b):
    'The golden formula'
    return 16 + (36*r + 6*g + b)


def rgb_row(row):
    return ''.join(rgb_cell(*cell) for cell in row)


def print_rgb_face(seq, padding_top=1, padding_bottom=1):
    for row in seq:
        for _ in range(padding_top):
            print(''.join(rgb_cell(*cell, pad=True) for cell in row))

        print(''.join(rgb_cell(*cell) for cell in row))

        for _ in range(padding_bottom):
            print(''.join(rgb_cell(*cell, pad=True) for cell in row))


def print_rgb_faces(faces, padding_top=1, padding_bottom=1):
    for face in faces:
        print_rgb_face(face, padding_top, padding_bottom)
        print('-'*40)


def print_planar_rgb_cube(faces):
    # print the planar form of the cube, e.g.
    #     0
    #   1 2
    #     3 4
    #     5
    empty_face = []
    for _ in range(6):
        empty_face.append(' '*8*6)

    string_faces = []
    for face in faces:
        string_faces.append([rgb_row(row) for row in face])

    flattened = [
        (empty_face, string_faces[0], empty_face),
        (string_faces[1], string_faces[2], empty_face),
        (empty_face, string_faces[3], string_faces[4]),
        (empty_face, string_faces[5], empty_face),
    ]

    for faces in flattened:
        for row in zip(*faces):
            print(''.join(list(itertools.chain(*row)))+RESET)


def test8():
    '''
    16-231:  6 × 6 × 6 cube (216 colors): 16 + 36 × r + 6 × g + b (0 ≤ r, g, b ≤ 5)
    '''
    all_seqs = {}

    seq = []
    for r in range(6):
        face = []
        for b in range(6):
            row = []
            for g in range(6):
                row.append((r, g, b))
            face.append(row)
        seq.append(face)
    all_seqs[('r', 'b', 'g')] = seq

    seq = []
    # # print('↓ b →  r |g')
    for g in range(6):
        face = []
        for b in range(6):
            row = []
            for r in range(6):
                row.append((r, g, b))
            face.append(row)
        seq.append(face)
    all_seqs[('g', 'b', 'r')] = seq

    seq = []
    for r in range(6):
        face = []
        for g in range(6):
            row = []
            for b in range(6):
                row.append((r, g, b))
            face.append(row)
        seq.append(face)
    all_seqs[('r', 'g', 'b')] = seq

    seq = []
    for b in range(6):
        face = []
        for g in range(6):
            row = []
            for r in range(6):
                row.append((r, g, b))
            face.append(row)
        seq.append(face)
    all_seqs[('b', 'g', 'r')] = seq

    seq = []
    for g in range(6):
        face = []
        for r in range(6):
            row = []
            for b in range(6):
                row.append((r, g, b))
            face.append(row)
        seq.append(face)
    all_seqs[('g', 'r', 'b')] = seq

    seq = []
    for b in range(6):
        face = []
        for r in range(6):
            row = []
            for g in range(6):
                row.append((r, g, b))
            face.append(row)
        seq.append(face)
    all_seqs[('r', 'b', 'g')] = seq

    # print('-'*80)
    # seq = []
    # for i in range(6):
    #     seq.append(
    #         list(reversed(all_seqs[('g', 'b', 'r')][i])) +
    #         all_seqs[('r', 'b', 'g')][i][1:] +
    #         all_seqs[('g', 'b', 'r')][(5*6)+i][1:]
    #     )
    # all_seqs['joined'] = seq

    for key, seq in all_seqs.items():
        print(key, '-'*80, sep='\n')
        print_rgb_faces(seq, padding_top=0)

    print_rgb_faces(all_seqs[('g', 'b', 'r')][:6])

    print('\n\n')
    print('planar faces', '-'*80, sep='\n')

    planar_faces = [
        rot90(all_seqs[('b','g','r')][5], 3),

        rot90(all_seqs[('g', 'b', 'r')][0], 2),
        rot90(all_seqs[('r', 'g', 'b')][0], 3),
        all_seqs[('r', 'b', 'g')][0],

        rot90(all_seqs[('g', 'b', 'r')][5], 1, flip=True),
        rot90(all_seqs[('r', 'g', 'b')][5], 1, flip=True),
    ]
    print_rgb_faces(planar_faces, padding_top=0)
    print_planar_rgb_cube(planar_faces)


rainbow1 = [
    (16, 52, 88, 124, 160, 196, 203, 210, 217, 224, 231),
    (16, 52, 88, 124, 160, 202, 209, 216, 223, 230, 231),
    (16, 52, 88, 124, 166, 208, 215, 222, 229, 230, 231),
    (16, 52, 88, 130, 172, 214, 221, 228, 229, 230, 231),
    (16, 52, 94, 136, 178, 220, 227, 228, 229, 230, 231),
    (16, 58, 100, 142, 184, 226, 227, 228, 229, 230, 231),
    (16, 22, 64, 106, 148, 190, 227, 228, 229, 230, 231),
    (16, 22, 28, 70, 112, 154, 191, 228, 229, 230, 231),
    (16, 22, 28, 34, 76, 118, 155, 192, 229, 230, 231),
    (16, 22, 28, 34, 40, 82, 119, 156, 193, 230, 231),
    (16, 22, 28, 34, 40, 46, 83, 120, 157, 194, 231),
    (16, 22, 28, 34, 40, 47, 84, 121, 158, 195, 231),
    (16, 22, 28, 34, 41, 48, 85, 122, 159, 195, 231),
    (16, 22, 28, 35, 42, 49, 86, 123, 159, 195, 231),
    (16, 22, 29, 36, 43, 50, 87, 123, 159, 195, 231),
    (16, 23, 30, 37, 44, 51, 87, 123, 159, 195, 231),
    (16, 17, 24, 31, 38, 45, 87, 123, 159, 195, 231),
    (16, 17, 18, 25, 32, 39, 81, 123, 159, 195, 231),
    (16, 17, 18, 19, 26, 33, 75, 117, 159, 195, 231),
    (16, 17, 18, 19, 20, 27, 69, 111, 153, 195, 231),
    (16, 17, 18, 19, 20, 21, 63, 105, 147, 189, 231),
    (16, 17, 18, 19, 20, 57, 99, 141, 183, 225, 231),
    (16, 17, 18, 19, 56, 93, 135, 177, 219, 225, 231),
    (16, 17, 18, 55, 92, 129, 171, 213, 219, 225, 231),
    (16, 17, 54, 91, 128, 165, 207, 213, 219, 225, 231),
    (16, 53, 90, 127, 164, 201, 207, 213, 219, 225, 231),
    (16, 52, 89, 126, 163, 200, 207, 213, 219, 225, 231),
    (16, 52, 88, 125, 162, 199, 206, 213, 219, 225, 231),
    (16, 52, 88, 124, 161, 198, 205, 212, 219, 225, 231),
    (16, 52, 88, 124, 160, 197, 204, 211, 218, 225, 231),
]
rainbow2 = [
    (59, 95, 131, 167, 174, 181, 188),
    (59, 95, 131, 173, 180, 187, 188),
    (59, 95, 137, 179, 186, 187, 188),
    (59, 101, 143, 185, 186, 187, 188),
    (59, 65, 107, 149, 186, 187, 188),
    (59, 65, 71, 113, 150, 187, 188),
    (59, 65, 71, 77, 114, 151, 188),
    (59, 65, 71, 78, 115, 152, 188),
    (59, 65, 72, 79, 116, 152, 188),
    (59, 66, 73, 80, 116, 152, 188),
    (59, 60, 67, 74, 116, 152, 188),
    (59, 60, 61, 68, 110, 152, 188),
    (59, 60, 61, 62, 104, 146, 188),
    (59, 60, 61, 98, 140, 182, 188),
    (59, 60, 97, 134, 176, 182, 188),
    (59, 96, 133, 170, 176, 182, 188),
    (59, 95, 132, 169, 176, 182, 188),
    (59, 95, 131, 168, 175, 182, 188),
]
pastels = [(102, 138, 144, 108, 109, 103, 139, 145)]
basics = [
    (0, 1, 3, 2, 6, 4, 5, 7),
    (8, 9, 11, 10, 14, 12, 13, 15),
]
greyscale = [
    (232, 233, 234, 235, 236, 237, 238, 239),
    (240, 241, 242, 243, 244, 245, 246, 247),
    (248, 249, 250, 251, 252, 253, 254, 255),
]

TESTS = (
    ('print sequential',                string_grid(test1())),
    ('test2',                           string_grid(list(test2()))),
    ('zigzag',                          string_grid(list(test3()))),
    ('zigzag2',                         string_grid(list(test4()))),
    ('single col zigzag',               string_grid(list(test5()))),
    ('single col zigzag, reverse odds', string_grid(list(test6()))),
    ('rainbow',                         string_grid(rainbow1)),
    ('pastel rainbow',                  string_grid(rainbow2)),
    ('pastels',                         string_grid(pastels)),
    ('basics',                          string_grid(basics)),
    ('greyscale',                       string_grid(greyscale)),
)


def run_tests(*groups):
    for g in groups:
        print_side_by_side(*['\n'.join([title, t]) for title, t in g])
        print('-'*80)


run_tests(*[[t] for t in TESTS])
print_grid([
    (16, 17, 18, 19, 20, 21, 27, 26, 25, 24, 23, 22,),
    (58, 59, 60, 61, 62, 63, 27, 26, 25, 24, 23, 22,)
])
print('-'*80)

test7()
test8()
