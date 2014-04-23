
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
A 2D polygon class for the ``mesh'' package.
'''

from __future__ import division
from math import atan2, pi
from vector2d import Vector2d
from vertex2d import Vertex2d
from line import Line

class Polygon(object):
    '''
    A class representing a 2D polygon.
    '''

    def __init__(self):
        self.clear()

    def clear(self):
        self.vertices = []
        self.lines = []
        self.next_vertex_name = 0
        self.next_line_name = 0

    def add_vertex(self, x, y=None):
        if isinstance(x, Vector2d):
            y = x.y
            x = x.x
        v = self.get_vertex(x, y)
        if v is None:
            v = Vertex2d(x, y, self.next_vertex_name)
            self.next_vertex_name += 1
            self.vertices.append(v)
            # check if the vertex lies on an existing line
            for l in self.lines:
                if l.contains(v):
                    # split the line into 2
                    v1, v2 = l.v1, l.v2
                    self.lines.remove(l)
                    self.add_line(v1, v)
                    self.add_line(v, v2)
                    break
        return v

    def add_line(self, v1, v2):
        l = Line(self.next_line_name, v1, v2)
        self.lines.append(l)
        for v in [v1, v2]:
            v.add_line(l)

    def area(self):
        v1, v2, v3 = self.vertices
        return (v2 - v1).cross(v3 - v1).magnitude() / 2.0

    def centroid(self):
        return reduce((lambda x,y:x+y), self.vertices) / 3

    def bounding_box(self):
        return ((min(v.x for v in self.vertices),
                 max(v.x for v in self.vertices)),
                (min(v.y for v in self.vertices),
                 max(v.y for v in self.vertices)))

    def closed(self):
        for v in self.vertices:
            if len(v.lines) < 2:
                return False
        return True

    def get_vertex(self, x, y=None):
        """Get a vertex from the mesh, if extant.
        
        :param x: x coordinate of the vertex, or optionally a list of coordinates.
        :keyword y: y coordinate of the vertex.

        XXX: this is currently very slow!
        """
        if not isinstance(x, Vector2d):
            x = Vector2d(x, y)

        for v in self.vertices:
            if v == x:
                return v

        return None

    def partition(self):

        # create bidirectional line segments from the polygon's lines
        lines = []
        for l in self.lines:
            v1, v2 = l.v1, l.v2
            theta1 = atan2(v2.y-v1.y, v2.x-v1.x)
            if theta1 < 0:
                theta1 += 2*pi
            theta2 = atan2(v1.y-v2.y, v1.x-v2.x)
            if theta2 < 0:
                theta2 += 2*pi
            lines.append((l.v1, l.v2, theta1))
            lines.append((l.v2, l.v1, theta2))

        # sort lines according to v1, then theta
        lines = sorted(lines, key=lambda x: (x[0].name, x[2]))

        #for l in lines:
        #    print "<v%i,v%i>, %.2fpi" % (l[0].name+1, l[1].name+1, l[2]/pi)

        # construct the wedges
        wedges = []
        for v in self.vertices:
            group = [l for l in lines if l[0] == v]
            wedges = wedges + [(group[i-1][1], group[i][0], group[i][1]) for i in range(len(group))]

        wedges = sorted(wedges, key=lambda x: (x[0].name, x[1].name))
        #for w in wedges:
        #    print "<v%i,v%i,v%i>" % (w[0].name+1, w[1].name+1, w[2].name+1)

        regions = []
        w_first = wedges[0]
        w_prev = w_first
        region = [w_first]
        wedges.remove(w_first)
        count = len(wedges)
        while count > 0:
            # find wedge with w_i+1[0], w_i+1[1] == w_i[1], w_i[2]
            try:
                w_next = [w for w in wedges if w[0]==w_prev[1] and w[1]==w_prev[2]][0]
                w_prev = w_next
                region.append(w_next)
                wedges.remove(w_next)
            except IndexError:
                regions.append(region)
                w_first = wedges[0]
                wedges.remove(w_first)
                w_prev = w_first
                region = [w_first]
            count -= 1
        # append the final region
        regions.append(region)

        # convert to paths (lists of vertices)
        paths = []
        for r in regions:
            path = []
            for w in r:
                path.append(w[0])
                #print "<v%i,v%i,v%i>" % (w[0].name+1, w[1].name+1, w[2].name+1)
            paths.append(path)

        return paths


