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

# Unit testing for the Vector class

from unittest import TestCase, main

from mesh import *
from mesh.plane import *


class PolygonClipTests(TestCase):

    def setUp(self):
        pass

    def test_clip(self):

        vs =  [Vector(50,150, 0),
               Vector(200,50,0),
               Vector(350,150,0),
               Vector(350,300,0),
               Vector(250,300,0),
               Vector(200,250,0),
               Vector(150,350,0),
               Vector(100,250,0),
               Vector(100,200,0)]

        clip = [Vector(100,100,0),
                Vector(300,100,0),
                Vector(300,300,0),
                Vector(100,300,0)]

        result = polygon_clip(vs, clip)

        answer = [Vector(100.0, 116.6666666667, 0.0),
                  Vector(125.0, 100.0000000000, 0.0),
                  Vector(275.0, 100.0000000000, 0.0),
                  Vector(300.0, 116.6666666667, 0.0),
                  Vector(300.0, 300.0000000000, 0.0),
                  Vector(250.0, 300.0000000000, 0.0),
                  Vector(200.0, 250.0000000000, 0.0),
                  Vector(175.0, 300.0000000000, 0.0),
                  Vector(125.0, 300.0000000000, 0.0),
                  Vector(100.0, 250.0000000000, 0.0),
                  Vector(100.0, 200.0000000000, 0.0)]

        self.assertEqual(result, answer)

        tri1 = [Vector(0,0,0), Vector(2,0,0), Vector(1,2,0)]
        tri2 = [Vector(0,2,0), Vector(1,0,0), Vector(2,2,0)]

        result = polygon_clip(tri1, tri2)

        answer = [Vector(0.5, 1.0, 0.0),
                  Vector(1.0, 0.0, 0.0),
                  Vector(1.5, 1.0, 0.0),
                  Vector(1.0, 2.0, 0.0)]

        self.assertEqual(result, answer)

        result = polygon_clip(tri1, tri1)
        self.assertEqual(result, tri1)

        tri3 = [Vector(0,2,0), Vector(2,2,0), Vector(1,4,0)]
        result = polygon_clip(tri1, tri3)
        self.assertEqual(result, [])

        

    def test_intersection(self):

        vs = [Vector(0, 1, 7), Vector(10, 1, 7)]
        vs2 = [Vector(5, -10, 7), Vector(5, 10, 7)]

        self.assertEqual(compute_line_intersection(vs, vs2), Vector(5, 1, 7))


    def test_sphere_line_intersection(self):

        tests = [(0.01, None), (0.2, True)]

        for test in tests:
            r = test[0]
            
            result = sphere_segment_intersect(Vector(1, 1.1, 1), r, [Vector(0,0,0), Vector(1, 1, 1).normalise()])

            self.assertEqual(result, test[1])


if __name__ == '__main__':
    main()

