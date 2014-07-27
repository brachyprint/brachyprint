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
Code intended to replace routes.py.

Describes piecewise-linear paths on a mesh.
"""

from collections import deque




class MeshPoint(object):
    """A point in a mesh. Has an field "point"."""

class VertexPoint(MeshPoint):
    """A point in a mesh which happens to be a vertex."""
    def __init__(self,v):
        self.point = v

class EdgePoint(MeshPoint):
    """A point in a mesh which happens to be on an edge."""
    def __init__(self,e,p):
        self.edge = e
        self.point = p

class FacePoint(MeshPoint):
    """A point in a mesh which is just on some face."""
    def __init__(self,f,p):
        self.face = f
        self.point = p



class Step(object):
    """A step along a face"""

    def __init__(self,face,p1,p2):
        self.face = face
        self.p1 = p1
        self.p2 = p2

    def dist(self):
        return self.p1.point.distance(self.p2.point)



class Route(object):
    """A path through a mesh.

    The "trajectory" field is a deque of steps.

    The "closed" field describes whether the route is a closed
    circle. If so, the beginning and end of the trajectory are
    expected to be the same.

    This has functionality which overlaps somewhat with that of
    src/mesh/routes.py
    """

    def __init__(self,l=[]):
        self.trajectory = deque(l)
        self.closed = False

    def __len__(self):
        return len(self.trajectory)

    def points(self):
        return [((t.p1.point.x, t.p1.point.y, t.p1.point.z), (t.p2.point.x, t.p2.point.y, t.p2.point.z)) for t in self.trajectory]

    def dist(self):
        return sum(s.dist() for s in self.trajectory)

    def extend_right(self,s):
        if self.closed:
            raise ValueError("Cannot extend closed route")
        self.trajectory.append(s)
        if self.trajectory[0].p1 == self.trajectory[-1].p2:
            self.closed=True

    def extend_left(self,f,t):
        if self.closed:
            raise ValueError("Cannot extend closed route")
        self.trajectory.append_left(s)
        if self.trajectory[0].p1 == self.trajectory[-1].p2:
            self.closed=True
