
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

    def faces_iter(self):
        if self.lface is not None:
            yield self.lface
        if self.rface is not None:
            yield self.rface

    def faces(self):
        return list(self.faces_iter())

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
    
