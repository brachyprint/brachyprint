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
Astar algorithm.
'''

from __future__ import division

class AStar:
    def __init__(self, s1, s2, mesh):
        self.s1 = s1
        self.s2 = s2
        self.t1 = mesh.faces[s1[3]]
        self.t2 = mesh.faces[s2[3]]
        self.d = {}
        for v in self.t1.vertices:
            self.add_node(((v.x - s1[0]) ** 2 + (v.y - s1[1]) ** 2 + (v.z - s1[2]) ** 2) ** 0.5, v)
        while True:
            self.d

    def add_node(self, dist, node):
        if not self.d.has_key(node) or self.d[node][0] > dist:
            self.d[node] = dist, dist + ((node.x - self.s2[0]) ** 2 + (node.y - self.s2[1]) ** 2 + (node.z - self.s2[2]) ** 2) * 0.5
        
        
