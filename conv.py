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
    for e in [edge, edge[::-1]]:
        for n, cube in collection.cubes.items():
            if n == face_name:
                continue
            f = cube.find_face_with_edge(e)
            if f:
                return f, n

def create_cube(f1, f1_name, cube_collection):
    f1_lhs = [r[0] for r in f1.rows]

    f2, f2_name = find_face_with_edge(cube_collection, f1_name, f1_lhs)
    f3, f3_name = find_face_with_edge(cube_collection, f1_name, f1[-1])
    f3_rhs = [row[-1] for row in f3]

    f4, f4_name = find_face_with_edge(cube_collection, f1_name, f1[0])
    f5, f5_name = find_face_with_edge(cube_collection, f3_name, f3_rhs)
    f6, f6_name = find_face_with_edge(cube_collection, f3_name, f3[-1])

    faces=[
        [gradient.Face.empty_face(6), f4.rot90(0, flip=True), gradient.Face.empty_face(6)],
        [f2.rot90(3, flip=True),      f1,                     gradient.Face.empty_face(6)],
        [gradient.Face.empty_face(6), f3,                     f5.rot90(1)],
        [gradient.Face.empty_face(6), f6,                     gradient.Face.empty_face(6)],
    ]
    gradient.Faces(faces).print()


coll = gradient.RGBCubeCollection({
    'rbg': gradient.RGBCube.from_ranges('r', 'b', 'g'),
    'brg': gradient.RGBCube.from_ranges('b', 'r', 'g'),
    'grb': gradient.RGBCube.from_ranges('g', 'r', 'b'),
})
f1 = coll.cubes['rbg'].faces.faces[0][0].rot90(0, flip=True)

create_cube(
    f1=f1,
    f1_name='rbg',
    cube_collection=coll
)
