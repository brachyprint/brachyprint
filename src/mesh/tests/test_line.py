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

# Unit testing for the Line class

from unittest import TestCase, main

from mesh import *


class BasicLineTests(TestCase):

    def setUp(self):
        v1 = Vector2d(1, 2)
        v2 = Vector2d(5, 6)

        self.l = Line(0, v1, v2)

    def test_contains(self):
        # list of vectors to test with the line, and whether they are on the
        # line or not
        vectors = [(0,1,False),
                   (1,2,False),
                   (2,3,True),
                   (2,2,False),
                   (4.5,5.5,True),
                   (4.99, 5.99, True),
                   (5,6,False),
                   (10,11,False),
                   (9,11,False),]

        for v in vectors:
            v1 = Vector2d(v[0], v[1])
            self.assertEqual(self.l.contains(v1), v[2])

        # test vertical lines
        l = Line(0, Vector2d(4, 4), Vector2d(4, -5))
        self.assertTrue(l.contains(Vector2d(4, 1)))

        # test horizontal lines
        l = Line(0, Vector2d(-4, 5), Vector2d(4, 5))
        self.assertTrue(l.contains(Vector2d(-2, 5)))


if __name__ == '__main__':
    main()

