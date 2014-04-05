
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
        self.normal = (v1 - v2).cross(v1 - v3)
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

