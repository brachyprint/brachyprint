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

# Unit testing for the Mesh class

from unittest import TestCase, main

from mesh import *
import os.path
import filecmp

class StlFormatTests(TestCase):

    def setUp(self):
        pass

    def test_read_ascii(self):

        path = os.path.dirname(__file__) 
        filename = path + "/cube.stl"

        m = Mesh()
        fileio.read_stl(m, filename)

        self.assertTrue(Vector(  0.0, 100.000000, 100.000000) is not None)
        self.assertTrue(Vector(  0.0, 100.000000,   0.000000) is not None)
        self.assertTrue(Vector(  0.0,   0.000000,   0.000000) is not None)
        self.assertTrue(Vector(  0.0,   0.000000, 100.000000) is not None)
        self.assertTrue(Vector(100.0,   0.000000,   0.000000) is not None)
        self.assertTrue(Vector(100.0,   0.000000, 100.000000) is not None)
        self.assertTrue(Vector(100.0, 100.000000,   0.000000) is not None)
        self.assertTrue(Vector(100.0, 100.000000, 100.000000) is not None)

        self.assertTrue(len(m.vertices) == 8)

        self.assertAlmostEqual(m.volume(), 1000000.0)
        self.assertAlmostEqual(m.surface_area(), 60000.0)
        self.assertTrue(m.closed())

        filename = path + "/sphere.stl"

        m = Mesh()
        fileio.read_stl(m, filename)

        m2 = Mesh()
        primitives.add_sphere(m2, 101)

        self.assertTrue(m.equivalent(m2))


    def test_write_ascii(self):
        path = os.path.dirname(__file__) 
        filename = path + "/cube_tmp.stl"
        filename_ref = path + "/cube.stl"

        m = Mesh()
        primitives.add_cube(m, 100)

        try:
            fileio.write_stl(m, filename, "Cube")

            # check the file was created
            self.assertTrue(os.path.isfile(filename))

            # check if it is the same as the reference file
            self.assertTrue(filecmp.cmp(filename, filename_ref))

        finally:
            if os.path.exists(filename):
                os.remove(filename)


if __name__ == '__main__':
    main()

