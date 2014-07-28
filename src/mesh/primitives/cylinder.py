
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
from math import pi, cos, sin

from mesh import Vector



def add_cylinder(mesh, radius, height,
                 n_circle = 10, n_height = 1,
                 v_axis = Vector(0,0,1),
                 basepoint = Vector(0,0,0),
                 twist_angle = 0,
                 close_bot = True,
                 close_top = True):
    """Add a cylinder to an existing mesh.

    Arguments are as follows:
    - mesh is the mesh to add to;
    - radius is the radius;
    - height is the height (expressed in multiples of v_axis);
    - n_circle is the number of points to place around a circle;
    - n_height is the number of layers to subdivide the cylinder into;
    - v_axis is a unit vector in the direction of the cylinder;
    - basepoint is a vector in the centre of the base of the cylinder;
    - twist_angle is the phase with which points are distributed;
    - close_bot and close_top say whether to give the circular disk
      ends of the cylinder.
    """

    v_axis = Vector(v_axis).normalise()
    (perp1, perp2) = v_axis.get_orthogonal_vectors()
    basepoint = Vector(basepoint)

    def make_row(i):
        for j in xrange(n_circle):
            t = twist_angle + (i+2*j)*pi/n_circle
            v = basepoint + perp1*(radius*cos(t)) + perp2*(radius*sin(t)) + v_axis*(height*i/n_height)
            yield mesh.add_vertex(v)

    r = list(make_row(0))

    if close_bot:
        o = mesh.add_vertex(basepoint)
        for j in xrange(n_circle):
            mesh.add_face(r[j],o,r[(j+1)%n_circle])

    for i in xrange(n_height):
        s = list(make_row(i+1))
        for j in xrange(n_circle):
            mesh.add_face(r[j],r[(j+1)%n_circle],s[j])
            mesh.add_face(s[(j-1)%n_circle],r[j],s[j])
        r = s

    if close_top:
        o = mesh.add_vertex(basepoint + v_axis*height)
        for j in xrange(n_circle):
            mesh.add_face(s[j],s[(j+1)%n_circle],o)
