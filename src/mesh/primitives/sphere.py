
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

def add_sphere(m, r, origin=Vector(0,0,0), detail_level=3):
    '''
    Add a cube to an existing mesh.

    Adapted from https://sites.google.com/site/dlampetest/python/triangulating-a-sphere-recursively

    :param: m -- Mesh() object
    :param: r -- radius
    '''

    octahedron_vertices = [ 
        Vector( 1.0, 0.0, 0.0), # 0 
        Vector(-1.0, 0.0, 0.0), # 1
        Vector( 0.0, 1.0, 0.0), # 2 
        Vector( 0.0,-1.0, 0.0), # 3
        Vector( 0.0, 0.0, 1.0), # 4 
        Vector( 0.0, 0.0,-1.0)  # 5                                
        ]
    octahedron_triangles = [ 
        [ 0, 2, 4 ],
        [ 2, 1, 4 ],
        [ 1, 3, 4 ],
        [ 3, 0, 4 ],
        [ 0, 5, 2 ],
        [ 2, 5, 1 ],
        [ 1, 5, 3 ],
        [ 3, 5, 0 ]]

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


    vertices, faces = octahedron_vertices, octahedron_triangles
    for i in range(detail_level - 1):
        vertices, faces = divide_all(vertices, faces)

    # create all the vertices
    for i in range(len(vertices)):
        v_e = m.get_vertex(vertices[i])
        if v_e is None:
            vertices[i] = m.add_vertex(vertices[i]*r + origin)
        else:
            vertices[i] = v_e

    # create all the faces
    for face in faces:
        m.add_face([vertices[index] for index in face])

