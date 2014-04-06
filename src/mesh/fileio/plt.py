
'''
Functions to read and write PLY files.

See https://en.wikipedia.org/wiki/PLY_%28file_format%29

read_ply(filename)
write_ply(mesh, filename)
'''

import re, struct
from mesh import *



def read_plt(filename):
    '''
    Create a mesh from a plt file.
    '''
    mesh = Mesh()
    with open(filename) as fp:
        lines = fp.readlines()
        for line in lines:
            n = line.split()
            mesh.add_vertex(float(n[0]), float(n[1]), float(n[2]))
    return mesh
    


