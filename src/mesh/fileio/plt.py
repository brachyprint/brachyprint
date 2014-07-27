#    Brachyprint -- 3D printing brachytherapy moulds
#    Copyright (C) 2013-14  James Cranch, Martin Green and Oliver Madge
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

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
    


