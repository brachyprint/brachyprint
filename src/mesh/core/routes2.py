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
from mesh import Vertex



class MeshPoint(object):
    """A point in a mesh. Has an field "point"."""

class VertexPoint(MeshPoint):
    """A point in a mesh which happens to be a vertex."""
    def __init__(self,v):
        self.point = v
    def splitmesh(self, mesh):
        return self.point

class EdgePoint(MeshPoint):
    """A point in a mesh which happens to be on an edge."""
    def __init__(self,e,p):
        self.edge = e
        self.point = p
    def splitmesh(self, mesh):
        v = Vertex(self.point.x, self.point.y, self.point.z)
        mesh.split_edge(v, self.edge)
        return v

class FacePoint(MeshPoint):
    """A point in a mesh which is just on some face."""
    def __init__(self,f,p):
        self.face = f
        self.point = p
    def splitmesh(self, mesh):
        v = Vertex(self.point.x, self.point.y, self.point.z)
        mesh.split_face(v, self.face)
        return v



class Step(object):
    """A step along a face"""

    def __init__(self,face,p1,p2):
        self.face = face
        self.p1 = p1
        self.p2 = p2

    def start(self):
	return self.p1.point

    def end(self):
        return self.p2.point

    def dist(self):
        return self.start().distance(self.end())



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

    def __iter__(self):
        return iter(self.trajectory)

    def __len__(self):
        return len(self.trajectory)

    def dist(self):
        return sum(s.dist() for s in self.trajectory)

    def points(self):
        yield self.trajectory[0].p1
        for s in self.trajectory:
            yield s.p2

    def faces_covered(self):
        return list(s.face for s in self.trajectory)

    def edges_crossed(self):
        for p in self.points():
            if isinstance(p,EdgePoint):
                yield p.edge

    def vertices_hit(self):
        for s in self.points():
            if isinstance(p,VertexPoint):
                yield p.point

    def start(self):
        return self.trajectory[0].start()

    def end(self):
        return self.trajectory[-1].end()

    def extend_right(self,s):
        if self.closed:
            raise ValueError("Cannot extend closed route")
        self.trajectory.append(s)
        if self.start() == self.end():
            self.closed=True

    def extend_left(self,f,t):
        if self.closed:
            raise ValueError("Cannot extend closed route")
        self.trajectory.append_left(s)
        if self.start() == self.end():
            self.closed=True
