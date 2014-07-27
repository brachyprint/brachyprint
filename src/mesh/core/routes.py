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

from math import sqrt

class point_to_point(object):
    def __init__(self, s, e, endPoint = None, endFace = None):
        self.s, self.e = s,e 
    def points(self):
        return [((self.s[0], self.s[1], self.s[2]), (self.e[0], self.e[1], self.e[2]))]
    def get_edges(self):
        return []

class point_to_vertex(object):
    def __init__(self, sx, sy, sz, e, endPoint = None, endFace = None):
        self.sx, self.sy, self.sz, self.e = sx, sy, sz, e
        self.endPoint, self.endFace = endPoint, endFace
    def dist(self):
        return sqrt((self.sx - self.e.x) ** 2 + (self.sy - self.e.y) ** 2 + (self.sz - self.e.z) ** 2) 
    def crowdist(self):
        return sqrt((self.e.x - self.endPoint[0]) ** 2 + (self.e.y - self.endPoint[1]) ** 2 + (self.e.z - self.endPoint[2]) ** 2)
    def end(self):
        return self.e
    def points(self):
        return [((self.sx, self.sy, self.sz), (self.e.x, self.e.y, self.e.z))]
    def new_Paths(self):
        results = [follow_edge(self.e, v, self.endPoint, self.endFace, edge) for v, edge in self.e.adjacent_vertices()] 
        if self.endPoint is not None and self.endFace in self.e.faces:
            results += [vertex_to_point(self.e, self.endPoint)]
        return results
    def finished(self):
        return False
    def get_edges(self):
        return []
    #def __str__(self):
     

class follow_edge(object):
    def __init__(self, s, e, endPoint = None, endFace = None, edge = None):
        self.s, self.e = s, e
        self.endPoint, self.endFace = endPoint, endFace
        self.edge = edge
    def dist(self):
        return sqrt((self.s.x - self.e.x) ** 2 + (self.s.y - self.e.y) ** 2 + (self.s.z - self.e.z) ** 2)
    def end(self):
        return self.e
    def points(self):
        return [((self.s.x, self.s.y, self.s.z), (self.e.x, self.e.y, self.e.z))]
    def new_Paths(self):
        results =  [follow_edge(self.e, v, self.endPoint, self.endFace, edge) for v, edge in self.e.adjacent_vertices()] 
        if self.endPoint is not None and self.endFace in self.e.faces:
            results += [vertex_to_point(self.e, self.endPoint)]
        return results
    def finished(self):
        return False
    def crowdist(self):
        return sqrt((self.e.x - self.endPoint[0]) ** 2 + (self.e.y - self.endPoint[1]) ** 2 + (self.e.z - self.endPoint[2]) ** 2)
    def get_edges(self):
        return [self.edge]

class vertex_to_point(object):
    def __init__(self, s, (ex, ey, ez)):
        self.s, self.ex, self.ey, self.ez = s, ex, ey, ez
    def dist(self):
        return sqrt((self.s.x - self.ex) ** 2 + (self.s.y - self.ey) ** 2 + (self.s.z - self.ez) ** 2)
    def finished(self):
        return True
    def points(self):
        return [((self.s.x, self.s.y, self.s.z), (self.ex, self.ey, self.ez))]
    def end(self):
        return "Finished!!!"
    def get_edges(self):
        return []
    def crowdist(self):
        return 0

class follow_edge_vertex_path(object):
    def __init__(self, start, end, edge, destination):
        self.start, self.end = start, end
        self.edge = edge
        self.destination = destination
    def dist(self):
        return sqrt((self.start.x - self.end.x) ** 2 + (self.start.y - self.end.y) ** 2 + (self.start.z - self.end.z) ** 2)
    def new_Paths(self):
        return  [follow_edge_vertex_path(self.end, v, edge, self.destination) for v, edge in self.end.adjacent_vertices()] 
    def finished(self):
        return (self.end == self.destination)
    def crowdist(self):
        return sqrt((self.end.x - self.destination.x) ** 2 + (self.end.y - self.destination.y) ** 2 + (self.end.z - self.destination.z) ** 2)
