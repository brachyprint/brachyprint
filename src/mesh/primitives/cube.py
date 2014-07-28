
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
A cube primitive.
'''

from __future__ import division

from mesh import Vector, nullVector
from cuboid import add_cuboid



def add_cube(mesh, l, n=1, vx=Vector(1,0,0), vy=Vector(0,1,0), vz=Vector(0,0,1), corner=nullVector):
    "Add a cube to an existing mesh."
    add_cuboid(mesh, l, l, l, n, n, n, vx, vy, vz, corner)
