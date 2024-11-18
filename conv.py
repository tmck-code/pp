#!/usr/bin/env python3

from pp import c, gradient

def find_face_with_edge(collection, face_name, face, edge_type):
    for n, cube in collection.cubes.items():
        if n == face_name:
            continue
        f = cube.find_face_with_edge(face, edge_type)
        if f:
            return f, n

def create_cube(f1, f1_name, cube_collection):
    f2, f2_name = find_face_with_edge(cube_collection, f1_name, f1, 'lhs')
    f3, f3_name = find_face_with_edge(cube_collection, f1_name, f1, 'bs')
    f4, f4_name = find_face_with_edge(cube_collection, f1_name, f1, 'ts')
    f5, f5_name = find_face_with_edge(cube_collection, f3_name, f3, 'rhs')
    f6, f6_name = find_face_with_edge(cube_collection, f3_name, f3, 'bs')

    faces=[
        [gradient.Face.empty_face(6), f4, gradient.Face.empty_face(6)],
        [f2,                          f1, gradient.Face.empty_face(6)],
        [gradient.Face.empty_face(6), f3, f5],
        [gradient.Face.empty_face(6), f6, gradient.Face.empty_face(6)],
    ]
    gradient.Faces(faces).print()

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
coll = gradient.RGBCubeCollection({
    'bgr': gradient.RGBCube.from_ranges('b', 'g', 'r'),
    'rgb': gradient.RGBCube.from_ranges('r', 'g', 'b'),
    'grb': gradient.RGBCube.from_ranges('g', 'r', 'b'),
})
coll.print()

for k in ('rgb', 'grb', 'bgr'):
    print('\n'+'~'*80+'\n')
    f1 = coll.cubes[k].faces.faces[0][0].rot90(0, flip=True)

    create_cube(
        f1=f1,
        f1_name=k,
        cube_collection=coll
    )
