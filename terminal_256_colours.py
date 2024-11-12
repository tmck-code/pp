#!/usr/bin/env python3

import json
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


def rgb_cell(r, g, b, pad=False, s=None, colors256=True):
    if s is None:
        if colors256:
            s = f' {16 + (36*r + 6*g + b):3d} '
        else:
            s = f'{16 + 36*r:3d},{6*g:2d},{b:d}'
    if pad:
        s = ' '*len(s)
    return colour_bg(s=s, n=(16 + (36*r + 6*g + b)))+RESET


def rgb_to_ansi(r, g, b):
    'The golden formula'
    return 16 + (36*r + 6*g + b)


def rgb_row(row, pad=False, s=None, colors256=True):
    return ''.join([rgb_cell(*cell, pad=pad, s=s, colors256=colors256) for cell in row])


def print_rgb_face(seq, padding_top=1, padding_bottom=1, colors256=True):
    for row in seq:
        for _ in range(padding_top):
            print(''.join(rgb_cell(*cell, pad=True, colors256=colors256)
                  for cell in row))

        print(''.join(rgb_cell(*cell, colors256=colors256) for cell in row))

        for _ in range(padding_bottom):
            print(''.join(rgb_cell(*cell, pad=True, colors256=colors256)
                  for cell in row))


def print_rgb_faces(faces, padding_top=1, padding_bottom=1, colors256=True):
    for face in faces:
        print_rgb_face(face, padding_top, padding_bottom, colors256)
        # print('-'*40)


def print_planar_rgb_cube(faces, blank=False, colors256=True):
    # print the planar form of the cube, e.g.
    #     0
    #   1 2
    #     3 4
    #     5
    if colors256:
        cell_width = 5
    else:
        cell_width = 8
    if blank:
        cell_width = 3
    empty_face = []
    for _ in range(6):
        empty_face.append(' '*cell_width*6)

    string_faces = []
    for face in faces:
        s = None
        if blank:
            s = ' '*cell_width
        string_faces.append(
            [rgb_row(row, s=s, pad=False, colors256=colors256) for row in face])

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
        print_rgb_faces(seq, padding_top=0)
        print(key, '-'*80, sep='\n')

    print_rgb_faces(all_seqs[('g', 'b', 'r')][:6])

    print('\n\n')
    print('planar faces', '-'*80, sep='\n')

    planar_faces = [
        rot90(all_seqs[('b', 'g', 'r')][5], 3),

        rot90(all_seqs[('g', 'b', 'r')][0], 2),
        rot90(all_seqs[('r', 'g', 'b')][0], 3),
        all_seqs[('r', 'b', 'g')][0],

        rot90(all_seqs[('g', 'b', 'r')][5], 1, flip=True),
        rot90(all_seqs[('r', 'g', 'b')][5], 1, flip=True),
    ]
    seen = set()
    for fi, face in enumerate(planar_faces):
        for y, row in enumerate(face):
            planar_faces[fi][y] = [cell for cell in row if cell not in seen]
            seen.update(row)

    print_rgb_faces(planar_faces, padding_top=0)
    print('-'*80)
    print_planar_rgb_cube(planar_faces)
    print('\n\n', '-'*80)
    print_planar_rgb_cube(planar_faces, colors256=False)
    print('\n\n', '-'*80)
    print_planar_rgb_cube(planar_faces, blank=True)
    print('\n\n', '-'*80)

    colours, dup_colours = {}, []
    for face in planar_faces:
        for row in face:
            for cell in row:
                colours[rgb_to_ansi(*cell)] = cell
                dup_colours.append(cell)
    print('total (dup)', len(dup_colours), json.dumps(dup_colours))

    all_colours = {}
    for r, g, b in itertools.product(range(6), repeat=3):
        all_colours[rgb_to_ansi(r, g, b)] = (r, g, b)
    print('all colours', len(all_colours), json.dumps(all_colours))

    colours = set(sorted(colours))
    print(colours)
    missing = set(range(16, 232)) ^ set(colours)
    print('total', len(colours))
    print('missing', len(missing), missing)

    for m in missing:
        print_cell(m)
        print(m, all_colours[m])
    print('\n', '-'*80)

    for face in itertools.batched(missing, 16):
        print_grid([face])
        print(''.join([colour_cell(cell)+RESET for cell in face]))
    print('\n', '-'*80)

    for c in [False, True]:
        print_rgb_face(
            all_seqs[('g', 'b', 'r')][1],
            colors256=c
        )
        print('\n', '-'*80)


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

# 64 missing/extra colours:
#  59    60    61    62    65    66    67    68    71    72    73    74    77    78    79    80
#  95    96    97    98   101   102   103   104   107   108   109   110   113   114   115   116
# 131   132   133   134   137   138   139   140   143   144   145   146   149   150   151   152
# 167   168   169   170   173   174   175   176   179   180   181   182   185   186   187   188

#   x   y    ?    y     y    n
#  22   58   94  130  166  202
#  23   59   95  131  167  203
#  24   60   96  132  168  204
#  25   61   97  133  169  205
#  26   62   98  134  170  206
#  27   63   99  135  171  207

experiment1 = (
    # --------------------------------#                                     # --------------------------------#
    ( 16,   16,   16,   16,   16,   16,  201,  207,  213,  219,  225,  231,   16,   16,   16,   16,   16,   16),
    ( 16,   16,   16,   16,   16,   16,  165,  171,  177,  183,  189,  195,   16,   16,   16,   16,   16,   16),
    ( 16,   16,   16,   16,   16,   16,  129,  135,  141,  147,  153,  159,   16,   16,   16,   16,   16,   16),
    ( 16,   16,   16,   16,   16,   16,   93,   99,  105,  111,  117,  123,   16,   16,   16,   16,   16,   16),
    ( 16,   16,   16,   16,   16,   16,   57,   63,   69,   75,   81,   87,   16,   16,   16,   16,   16,   16), #
    ( 16,   16,   16,   16,   16,   16,   21,   27,   33,   39,   45,   51,   16,   16,   16,   16,   16,   16), #
    (201,  165,  129,   93,   57,   21,   21,   27,   33,   39,   45,   51,   16,   16,   16,   16,   16,   16), #
    (200,  164,  128,   92,   56,   20,   20,   26,   32,   38,   44,   50,   16,   16,   16,   16,   16,   16), #
    (199,  163,  127,   91,   55,   19,   19,   25,   31,   37,   43,   49,   16,   16,   16,   16,   16,   16), #
    (198,  162,  126,   90,   54,   18,   18,   24,   30,   36,   42,   48,   16,   16,   16,   16,   16,   16), #
    (197,  161,  125,   89,   53,   17,   17,   23,   29,   35,   41,   47,   16,   16,   16,   16,   16,   16), #
    (196,  160,  124,   88,   52,   16,   16,   22,   28,   34,   40,   46,   16,   16,   16,   16,   16,   16), #
    ( 16,   16,   16,   16,   16,   16,   16,   22,   28,   34,   40,   46,   46,   47,   48,   49,   50,   51),
    ( 16,   16,   16,   16,   16,   16,   52,   58,   64,   70,   76,   82,   82,   83,   84,   85,   86,   87),
    ( 16,   16,   16,   16,   16,   16,   88,   94,  100,  106,  112,  118,  118,  119,  120,  121,  122,  123),
    ( 16,   16,   16,   16,   16,   16,  124,  130,  136,  142,  148,  154,  154,  155,  156,  157,  158,  159),
    ( 16,   16,   16,   16,   16,   16,  160,  166,  172,  178,  184,  190,  190,  191,  192,  193,  194,  195),
    ( 16,   16,   16,   16,   16,   16,  196,  202,  208,  214,  220,  226,  226,  227,  228,  229,  230,  231),
    ( 16,   16,   16,   16,   16,   16,  196,  202,  208,  214,  220,  226,   16,   16,   16,   16,   16,   16), #
    ( 16,   16,   16,   16,   16,   16,  197,  203,  209,  215,  221,  227,   16,   16,   16,   16,   16,   16), #
    ( 16,   16,   16,   16,   16,   16,  198,  204,  210,  216,  222,  228,   16,   16,   16,   16,   16,   16), #
    ( 16,   16,   16,   16,   16,   16,  199,  205,  211,  217,  223,  229,   16,   16,   16,   16,   16,   16), #
    ( 16,   16,   16,   16,   16,   16,  200,  206,  212,  218,  224,  230,   16,   16,   16,   16,   16,   16), #
    ( 16,   16,   16,   16,   16,   16,  201,  207,  213,  219,  225,  231,   16,   16,   16,   16,   16,   16), #
)

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

# run experiment 1
run_tests([('experiment1', string_grid(experiment1))])
