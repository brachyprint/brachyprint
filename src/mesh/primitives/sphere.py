
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
A sphere primitive.
'''

from __future__ import division

from mesh import Vector
from math import sqrt

def add_sphere(m, r, origin=Vector(0,0,0), detail_level=3):
    '''
    Add a sphere to an existing mesh.

    Adapted from https://sites.google.com/site/dlampetest/python/triangulating-a-sphere-recursively

    :param: m -- Mesh() object
    :param: r -- radius
    '''

    psi = (1.0 + sqrt(5))/2

    icosahedron_vertices = [ 
        Vector(-1.0, 0.0, psi), # 0
        Vector( 1.0, 0.0, psi), # 1
        Vector(-1.0, 0.0,-psi), # 2
        Vector( 1.0, 0.0,-psi), # 3

        Vector( 0.0, psi, 1.0), # 4
        Vector( 0.0, psi,-1.0), # 5
        Vector( 0.0,-psi, 1.0), # 6
        Vector( 0.0,-psi,-1.0), # 7

        Vector( psi, 1.0, 0.0), # 8
        Vector(-psi, 1.0, 0.0), # 9
        Vector( psi,-1.0, 0.0), # 10
        Vector(-psi,-1.0, 0.0)  # 11
        ]

    for i in range(len(icosahedron_vertices)):
        icosahedron_vertices[i] = icosahedron_vertices[i].normalise()

    icosahedron_triangles = [ 
        #[0,4,1],  [0,9,4],  [9,5,4],  [4,5,8],  [4,8,1],    
        [0,1,4],  [0,4,9],  [9,4,5],  [4,8,5],  [4,1,8],    
        #[8,10,1], [8,3,10], [5,3,8],  [5,2,3],  [2,7,3],    
        [8,1,10], [8,10,3], [5,8,3],  [5,3,2],  [2,3,7],    
        #[7,10,3], [7,6,10], [7,11,6], [11,0,6], [0,1,6], 
        [7,3,10], [7,10,6], [7,6,11], [11,6,0], [0,6,1], 
        #[6,1,10], [9,0,11], [9,11,2], [9,2,5],  [7,2,11]]
        [6,10,1], [9,11,0], [9,2,11], [9,5,2],  [7,11,2]]

    def divide_all( vertices, triangles ):    
        # Subdivide each triangle in the old approximation and normalize
        #  the new points thus generated to lie on the surface of the unit
        #  sphere.
        # Each input triangle with vertices labelled [0,1,2] as shown
        #  below will be turned into four new triangles:
        #
        #            Make new points
        #                 a = (0+2)/2
        #                 b = (0+1)/2
        #                 c = (1+2)/2
        #        1
        #       /\        Normalize a, b, c
        #      /  \
        #    b/____\ c    Construct new triangles
        #    /\    /\       t1 [0,b,a]
        #   /  \  /  \      t2 [b,1,c]
        #  /____\/____\     t3 [a,b,c]
        # 0      a     2    t4 [a,c,2]    

        v_new = vertices
        faces = []
        for f in triangles:
            # extract vertices
            v0 = vertices[f[0]]
            v1 = vertices[f[1]]
            v2 = vertices[f[2]]

            # construct new vertices
            a = (v0 + v2) * 0.5
            b = (v0 + v1) * 0.5
            c = (v1 + v2) * 0.5
            a = a.normalise()
            b = b.normalise()
            c = c.normalise()
            v_new.append(a); a_i = len(v_new)-1
            v_new.append(b); b_i = len(v_new)-1
            v_new.append(c); c_i = len(v_new)-1

            # construct the 4 new faces
            faces.append([f[0], b_i, a_i])
            faces.append([b_i, f[1], c_i])
            faces.append([a_i, b_i, c_i])
            faces.append([a_i, c_i, f[2]])

        return v_new, faces


    vertices, faces = icosahedron_vertices, icosahedron_triangles
    for i in range(detail_level - 1):
        vertices, faces = divide_all(vertices, faces)

    # apply a translation to the vertices
    for i in range(len(vertices)):
        vertices[i] = vertices[i]*r + origin

    # create all the vertices
    for i in range(len(vertices)):
        v_e = m.get_vertex(vertices[i])
        if v_e is None:
            vertices[i] = m.add_vertex(vertices[i])
        else:
            vertices[i] = v_e

    # create all the faces
    for face in faces:
        m.add_face([vertices[index] for index in face])

