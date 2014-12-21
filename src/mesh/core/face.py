
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
A face class for the ``mesh'' package.
'''

from __future__ import division

class Face(object):
    '''
    A class representing a mesh face.
    '''

    def __init__(self, name, v1, v2, v3):
        self.name = name
        self.vertices = v1, v2, v3
        self.normal = (v1 - v2).cross(v1 - v3).normalise()
        self.volume = None
        self.edges = []

    def add_edge(self, edge):
        self.edges.append(edge)

    def signed_volume(self):
        v1, v2, v3 = self.vertices
        return v1.dot(v2.cross(v3)) / 6.0

    def area(self):
        v1, v2, v3 = self.vertices
        return (v2 - v1).cross(v3 - v1).magnitude() / 2.0

    def centroid(self):
        return reduce((lambda x,y:x+y), self.vertices) / 3

    def bounding_box(self, tolerance = 0):
        return ((min(v.x for v in self.vertices) - tolerance,
                 max(v.x for v in self.vertices) + tolerance),
                (min(v.y for v in self.vertices) - tolerance,
                 max(v.y for v in self.vertices) + tolerance),
                (min(v.z for v in self.vertices) - tolerance,
                 max(v.z for v in self.vertices) + tolerance))

    def nearest_vertex(self, x, y, z):
        return min([((v.x - x) ** 2 + (v.y - y) ** 2 + (v.z - z) ** 2, v) for v in self.vertices])[1]
        
    def project2d(self):
        # form basis vectors
        a = (self.vertices[1]-self.vertices[0])
        b = (self.vertices[2]-self.vertices[0])
        n = b.cross(a)
        u = a
        v = n.cross(u)
        u = u.normalise()
        v = v.normalise()
        n = u.cross(v)
        origin = self.vertices[0]

        fun = lambda vs: [vec.x*u+vec.y*v+origin for vec in vs]

        return ([f.project2dvector(u,v) for f in self.vertices], u, v, fun)

    def opposite_edge(self, vertex):
        try:
            return next(e for e in self.edges if e.v1 != vertex and e.v2 != vertex)
        except:
            print vertex
            for e in self.edges:
                print e.v1, e.v2
            raise Exception("No Opposite Edge ?!?")

    def neighbouring_faces(self):
        """Generates the faces which are adjacent to this one.
        """
        for e in self.edges:
            f = e.face_on_other_side(self)
            if f is not None:
                yield f

    def parallel_plate(self, epsilon=0.00001):
        """Returns the set of all contiguous faces, starting with this one,
        that lie in the same plane.
        """
        old = set()
        new = set([self])
        while new:
            f = new.pop()
            old.add(f)
            for g in f.neighbouring_faces():
                if g not in old and g not in new and f.normal.cross(g.normal).magnitude() < epsilon:
                    new.add(g)
        return old
