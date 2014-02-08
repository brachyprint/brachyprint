
from __future__ import division

def make_cube(c, d, offset=[0,0,0]):
    '''
    Add a cube to an existing mesh.
    '''

    # create the 8 corner vertices
    vs = [(0,0,0), (0,0,d), (d,0,0), (d,0,d), (d,d,0), (d,d,d), (0,d,0), (0,d,d)]
    vertices = [c.add_vertex(x+offset[0], y+offset[1], z+offset[2]) for x,y,z in vs]

    # create side faces
    for i in range(len(vertices)):
        if i % 2 == 1:
            c.add_face(vertices[i-2], vertices[i-1], vertices[i])
        else:
            c.add_face(vertices[i-1], vertices[i-2], vertices[i])

    # create end faces
    for i in [0, 1, 4, 5]:
        if i % 2 == 1:
            c.add_face(vertices[i-2], vertices[i], vertices[i+2])
        else:
            c.add_face(vertices[i+2], vertices[i], vertices[i-2])

