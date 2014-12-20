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

"""
Mesh
====

Provides
  1. A 3D Vector<> class
  2. A mesh data structure for efficient mesh operations
  3. Functions to create 3D primitives (e.g. cylinders, spheres, cubes)
  4. Mesh manipulations, e.g. clipping, inside/outside, intersection

Available subpackages
---------------------
primitives
    primitive generators
manipulate
    mesh manipulations

Utilities
---------
tests
    Run mesh unittests

"""

from core import Mesh, Vector, nullVector, Vertex, Face, Edge
from core import Polygon, Vector2d, nullVector2d, Vertex2d, Line
from plane import *

# subpackages
import primitives
import manipulate
import fileio

