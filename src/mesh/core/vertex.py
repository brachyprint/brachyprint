
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
A 3D vertex class for the ``mesh'' package.
'''

from __future__ import division

from vector import Vector, nullVector

class Vertex(Vector):
    '''
    A class representing a mesh vertex.
    '''

    def __init__(self, x, y, z):
        super(Vertex, self).__init__(x, y, z)
        self.edges = []
        self.faces = []

    def __repr__(self):
        return "<Vertex x:%f y:%f z:%f>" % (self.x, self.y, self.z)

    def __hash__(self):
        return id(self)

    def __str__(self):
        return "<Vertex (%f,%f,%f)>"%(self.x, self.y, self.z)


    def add_edge(self, edge):
        '''
        Associate an edge with the vertex.
        '''
        self.edges.append(edge)

    def add_face(self, face):
        '''
        Associate a face with the vertex.
        '''
        self.faces.append(face)

    def remove_face(self, face):
        """
        Associate a face with the vertex no longer.
        """
        self.faces.remove(face)

    def normal(self):
        '''Determine a normal at the vertex by averaging its associated face
        normals.
        '''
        n = sum([f.normal for f in self.faces], nullVector)
        return n.normalise()

    def adjacent_vertices(self):
        '''
        Return (vertex, edge) for all adjacent vertices.
        '''
        return [(e.v1, e) for e in self.edges if e.v2 is self] + [(e.v2, e) for e in self.edges if e.v1 is self]

