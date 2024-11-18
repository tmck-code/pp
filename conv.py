#!/usr/bin/env python3

from pp import c, gradient

for i in range(16, 232):
    cell = c.from_ansi(i)
    print(f'{i:3d} {str(cell.rgb):>16s}', cell.colorise(' '*8))


print('\n'+'~'*80+'\n')

coll=gradient.RGBCubeCollection({
    'rgb': gradient.RGBCube.from_ranges('r', 'g', 'b'),
    'brg': gradient.RGBCube.from_ranges('b', 'r', 'g'),
    'grb': gradient.RGBCube.from_ranges('g', 'r', 'b'),
})
coll.print()

print('\n'+'~'*80+'\n')

c1 = gradient.RGBCube.from_ranges('r', 'b', 'g')
c2 = gradient.RGBCube.from_ranges('g', 'r', 'b')
c3 = gradient.RGBCube.from_ranges('b', 'r', 'g')

def find_face_with_edge(collection, face_name, edge):
    for e, flip in [(edge, False), (edge[::-1], True)]:
        for n, cube in collection.cubes.items():
            if n == face_name:
                continue
            f = cube.find_face_with_edge(e)
            if f:
                return f.rot90(0, flip=flip), n

def create_cube(f1, f1_name, cube_collection):
    f1_lhs = [r[0] for r in f1.rows]

    f2, f2_name = find_face_with_edge(cube_collection, f1_name, f1_lhs)
    f2 = f2.rot90(1, flip=True)
    print('f2', f2_name)
    f2.print()
    f3, f3_name = find_face_with_edge(cube_collection, f1_name, f1[-1])
    # f3 = f3.rot90(0, flip=True)
    print('f3', f3_name)
    f3.print()
    f3_rhs = [row[-1] for row in f3]

    f4, f4_name = find_face_with_edge(cube_collection, f1_name, f1[0])
    f4 = f4.rot90(0, flip=True)
    print('f4', f4_name)
    f4.print()
    f5, f5_name = find_face_with_edge(cube_collection, f3_name, f3_rhs)
    f5 = f5.rot90(3)
    print('f5', f5_name)
    f5.print()
    print(f3[-1])
    f6, f6_name = find_face_with_edge(cube_collection, f3_name, f3[-1])
    f6 = f6.rot90(2, flip=True)
    print('f6', f6_name)
    f6.print()

    faces=[
        [gradient.Face.empty_face(6), f4, gradient.Face.empty_face(6)],
        [f2,                          f1,                     gradient.Face.empty_face(6)],
        [gradient.Face.empty_face(6), f3,                     f5],
        [gradient.Face.empty_face(6), f6,                     gradient.Face.empty_face(6)],
    ]
    gradient.Faces(faces).print()


coll = gradient.RGBCubeCollection({
    'brg': gradient.RGBCube.from_ranges('b', 'r', 'g'),
    'rgb': gradient.RGBCube.from_ranges('r', 'g', 'b'),
    'grb': gradient.RGBCube.from_ranges('g', 'r', 'b'),
})
coll.print()
f1 = coll.cubes['rgb'].faces.faces[0][0].rot90(0, flip=True)

create_cube(
    f1=f1,
    f1_name='rgb',
    cube_collection=coll
)
