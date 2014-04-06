# Unit testing for the Mesh class

from unittest import TestCase, main

from mesh import *


class BasicMeshTests(TestCase):

    def setUp(self):
        pass

    def test_create(self):
        m = Mesh()

        # add a vertex by vector
        v1 = Vector(-1,-5,-3)
        v1 = m.add_vertex(v1)

        self.assertTrue(len(m.vertices) == 1)

        # add a vertex by coordinate
        v2 = m.add_vertex(0,1,-6)
        self.assertTrue(len(m.vertices) == 2)

        v3 = m.add_vertex(5,1,1)
        self.assertTrue(len(m.vertices) == 3)

        m.add_face(v1, v2, v3)
        self.assertTrue(len(m.faces) == 1)

        # check face order is preserved
        self.assertTrue(m.faces[0].vertices[0] == v1)
        self.assertTrue(m.faces[0].vertices[1] == v2)
        self.assertTrue(m.faces[0].vertices[2] == v3)

        # check edges are all present
        self.assertTrue(m.edges.has_key((v1, v2)))
        self.assertTrue(m.edges.has_key((v2, v3)))
        self.assertTrue(m.edges.has_key((v3, v1)))

        # check that vertices are al present in the mesh
        self.assertEqual(m.get_vertex(v1), v1)
        self.assertEqual(m.get_vertex(v2), v2)
        self.assertEqual(m.get_vertex(v3), v3)
        v4 = Vector(-17,3,-3)
        self.assertEqual(m.get_vertex(v4), None)

        # check max and min are being calculated correctly
        self.assertTrue(m.minX==-1)
        self.assertTrue(m.maxX==5)
        self.assertTrue(m.minY==-5)
        self.assertTrue(m.maxY==1)
        self.assertTrue(m.minZ==-6)
        self.assertTrue(m.maxZ==1)


if __name__ == '__main__':
    main()

