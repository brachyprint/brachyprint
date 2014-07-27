
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
An edge class for the ``mesh'' package.
'''

from __future__ import division

class Edge(object):
    '''
    A class representing a mesh edge.
    '''

    def __init__(self, v1, v2):
        self.v1, self.v2 = v1, v2
        self.lface = None
        self.rface = None
        v1.add_edge(self)
        v2.add_edge(self)

    def displacement(self):
        return self.v2 - self.v1

    def faces_iter(self):
        if self.lface is not None:
            yield self.lface
        if self.rface is not None:
            yield self.rface

    def faces(self):
        return list(self.faces_iter())

    def face_on_other_side(self,f):
        if self.lface == f:
            return self.rface
        else:
            return self.lface

    def add_face(self, face, isleft=None):
        if isleft is None:
            v = (self.v1, self.v2)
            (u1,u2,u3) = face.vertices
            isleft = (v == (u1,u2)) or (v == (u2,u3)) or (v == (u3,u1))
        if isleft:
            if self.lface is None:
                self.lface = face
            else:
                raise ValueError("Edge already has an associated left face")
        else:
            if self.rface is None:
                self.rface = face
            else:
                raise ValueError("Edge already has an associated right face")

    def remove_face(self, face):
        if self.lface is face:
            self.lface = None
            return None
        if self.rface is face:
            self.rface = None
            return None
        raise ValueError("Edge does not attach to the face to be removed")
    
    def to_ratio(self, v):
        """
        (Assuming v lies on this edge), how far of the way along does
        it lie? Calling this on v1 yields 0.0, and calling it on v2
        yields 1.0.
        """
        d = self.displacement()
        return (v-self.v1).dot(d) / d.magnitude()

    def from_ratio(self, i):
        """
        Return a vector i of the way from v1 to v2.
        """
        return self.v2*i + self.v1*(1-i)

    def zero_point(self, fn):
        """Return a vector along the line at which linear functional fn
        vanishes.
        """
        a1 = fn(self.v1)
        a2 = fn(self.v2)
        return (a2*self.v1 - a1*self.v2)/(a2-a1)
