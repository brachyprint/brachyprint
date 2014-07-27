
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
A cylinder primitive.
'''

from __future__ import division

import mesh
from math import pi, cos, sin

class transform_and_add_vertex(object):
    def __init__(self, mesh, offset, axis, perp1, perp2):
        self.mesh = mesh
        self.offset = offset
        self.axis = axis
        self.perp1 = perp1
        self.perp2 = perp2
    def __call__(self, x, y, z):
        return self.mesh.add_vertex(*[o + x * p1 + y * p2 + z * a 
                                      for o, p1, p2, a 
                                      in zip(self.offset, self.perp1, self.perp2, self.axis)])

def add_cylinder(c, r, h, sampling, axis=(0, 0, 1), offset=(0,0,0)):
    '''
    Add a cylinder of radius r and height h to the existing mesh c.
    '''

    axis = mesh.Vector(axis)
    offset = mesh.Vector(offset)

    #Find a normalised orthogonal set of vectors
    axis = axis.normalise()
    for arbitary_vector in [mesh.Vector(0, 0, 1), mesh.Vector(0, 1, 0), mesh.Vector(1, 0, 0)]:
        if arbitary_vector.dot(axis) < 0.6:  #One of the above vectors dot producted with a normalised vector must be less than 1/3 ** 1/2
            perp1 = arbitary_vector.cross(axis).normalise()
            perp2 = axis.cross(perp1).normalise()
            break
    add_vertex = transform_and_add_vertex(c, offset, axis, perp1, perp2)
    # create end vertices

    o = add_vertex(0, 0, 0)
    o2 = add_vertex(0, 0, h)

    vs = []

    hs = [0, h]

    for j in range(2):
        vs.append([])
        for i in range(sampling):
            th = i/sampling*2*pi
            x = r*sin(th)
            y = r*cos(th)
            vs[j].append(add_vertex(x,y,hs[j])) # bottom

    v = vs[0]
    v2 = vs[1]
    for i in range(len(v)):
        c.add_face([v[i], v[i-1], v2[i-1], v2[i]])
    
    # create bottom
    for i in range(len(vs[0])):
        c.add_face(vs[0][i-1],vs[0][i],o)

    # create top
    for i in range(len(vs[-1])):
        c.add_face(vs[-1][i],vs[-1][i-1],o2)

    return c 

