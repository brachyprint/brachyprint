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

from __future__ import division

from math import pi, cos, sin

from mesh import Vector


def add_torus(m, r_out, r_in, meridians, parallels, x_axis=Vector(1,0,0), y_axis=Vector(0,1,0), z_axis=Vector(0,0,1), meridian_phase=0, parallel_phase=0, offset=Vector(0,0,0)):
    """
    Add a torus of inner radius r_out and outer radius r_in to the
    existing mesh m.

    More precisely it approximates the manifold parametrised by
      x = (r_out + r_in*cos(theta))*cos(phi)
      y = (r_out + r_in*cos(theta))*sin(phi)
      z = r_in*sin(theta)

    The approximation is based the given number of meridians and
    parallels, with squares subdivided into two triangles, and thus
    uses 2*meridians*parallels triangular faces.
    """

    def make_vertex(i,j):
        theta = 2*pi*i/parallels + parallel_phase
        phi = 2*pi*j/meridians + meridian_phase
        p = x_axis*((r_out + r_in*cos(theta))*cos(phi)) + \
            y_axis*((r_out + r_in*cos(theta))*sin(phi)) + \
            z_axis*(r_in*sin(theta)) + \
            offset
        return m.add_vertex(p.x,p.y,p.z)

    vertices = [[make_vertex(i,j) for j in xrange(meridians)] for i in xrange(parallels)]

    for i in xrange(parallels):
        for j in xrange(meridians):
            v0 = vertices[(i+0)%parallels][(j+0)%meridians]
            v1 = vertices[(i+0)%parallels][(j+1)%meridians]
            v2 = vertices[(i+1)%parallels][(j+1)%meridians]
            v3 = vertices[(i+1)%parallels][(j+0)%meridians]
            m.add_face([v0,v1,v2])
            m.add_face([v2,v3,v0])
