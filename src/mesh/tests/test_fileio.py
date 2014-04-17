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

