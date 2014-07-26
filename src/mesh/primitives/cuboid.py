
#    Brachyprint -- 3D printing brachytherapy moulds
#    Copyright (C) 2013-14  Martin Green and Oliver Madge
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
A cube primitive.
'''

from __future__ import division

def add_cuboid(c, x, y, z, offset=[0,0,0]):
    '''
    Add a cube to an existing mesh.
    '''

    # create the 8 corner vertices
    vs = [(0,0,0), (0,0,z), (x,0,0), (x,0,z), (x,y,0), (x,y,z), (0,y,0), (0,y,z)]
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

