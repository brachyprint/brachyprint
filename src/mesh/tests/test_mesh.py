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

        # check that vertices are all present in the mesh
        print "left: %s"%(m.get_vertex(v1),)
        print "right: %s"%(v1,)
        self.assertEqual(m.get_vertex(v1), v1.name)
        self.assertEqual(m.get_vertex(v2), v2.name)
        self.assertEqual(m.get_vertex(v3), v3.name)
        v4 = Vector(-17,3,-3)
        self.assertIsNone(m.get_vertex(v4))

        # check max and min are being calculated correctly
        self.assertTrue(m.minX==-1)
        self.assertTrue(m.maxX==5)
        self.assertTrue(m.minY==-5)
        self.assertTrue(m.maxY==1)
        self.assertTrue(m.minZ==-6)
        self.assertTrue(m.maxZ==1)

class MergeMeshTests(TestCase):

    def setUp(self):
        pass

    def test_merge(self):
        m1 = Mesh()
        v11 = m1.add_vertex(-1,-5,-3)
        v12 = m1.add_vertex(0,1,-6)
        v13 = m1.add_vertex(5,1,1)
        m1.add_face(v11, v12, v13)

        m2 = Mesh()
        v21 = m2.add_vertex(-41,-50,-36)
        v22 = m2.add_vertex(40,122,-60)
        v23 = m2.add_vertex(35,177,100)
        m2.add_face(v21, v22, v23)

        m1.add_mesh(m2)

        # check face order is preserved
        self.assertTrue(m1.faces[0].vertices[0] == v11)
        self.assertTrue(m1.faces[0].vertices[1] == v12)
        self.assertTrue(m1.faces[0].vertices[2] == v13)
        self.assertTrue(m1.faces[0].vertices[0] is v11)
        self.assertTrue(m1.faces[0].vertices[1] is v12)
        self.assertTrue(m1.faces[0].vertices[2] is v13)
        self.assertTrue(m1.faces[1].vertices[0] == v21)
        self.assertTrue(m1.faces[1].vertices[1] == v22)
        self.assertTrue(m1.faces[1].vertices[2] == v23)

        # check vertices have been cloned
        self.assertTrue(m1.faces[1].vertices[0] is not v21)
        self.assertTrue(m1.faces[1].vertices[1] is not v22)
        self.assertTrue(m1.faces[1].vertices[2] is not v23)

        # check edges are all present
        self.assertTrue(m1.edges.has_key((v11, v12)))
        self.assertTrue(m1.edges.has_key((v12, v13)))
        self.assertTrue(m1.edges.has_key((v13, v11)))
        self.assertTrue(m1.edges.has_key((m1.faces[1].vertices[0], m1.faces[1].vertices[1])))
        self.assertTrue(m1.edges.has_key((m1.faces[1].vertices[1], m1.faces[1].vertices[2])))
        self.assertTrue(m1.edges.has_key((m1.faces[1].vertices[2], m1.faces[1].vertices[0])))

        # check original edges are not present
        self.assertFalse(m1.edges.has_key((v21, v22)))
        self.assertFalse(m1.edges.has_key((v22, v23)))
        self.assertFalse(m1.edges.has_key((v23, v21)))
         
        # check max and min are being calculated correctly
        self.assertTrue(m1.minX==-41)
        self.assertTrue(m1.maxX==40)
        self.assertTrue(m1.minY==-50)
        self.assertTrue(m1.maxY==177)
        self.assertTrue(m1.minZ==-60)
        self.assertTrue(m1.maxZ==100)

    def test_merge_invert(self):
        m1 = Mesh()
        v11 = m1.add_vertex(-1,-5,-3)
        v12 = m1.add_vertex(0,1,-6)
        v13 = m1.add_vertex(5,1,1)
        m1.add_face(v11, v12, v13)

        m2 = Mesh()
        v21 = m2.add_vertex(-41,-50,-36)
        v22 = m2.add_vertex(40,122,-60)
        v23 = m2.add_vertex(35,177,100)
        m2.add_face(v21, v22, v23)

        m1.add_mesh(m2, invert = True)

        # check face order is reversed
        self.assertTrue(m1.faces[1].vertices[0] == v21)
        self.assertTrue(m1.faces[1].vertices[1] == v23)
        self.assertTrue(m1.faces[1].vertices[2] == v22)

        # check verticies have been cloned
        self.assertTrue(m1.faces[1].vertices[0] is not v21)
        self.assertTrue(m1.faces[1].vertices[1] is not v23)
        self.assertTrue(m1.faces[1].vertices[2] is not v22)

        # check edges are all present
        self.assertTrue(m1.edges.has_key((v11, v12)))
        self.assertTrue(m1.edges.has_key((v12, v13)))
        self.assertTrue(m1.edges.has_key((v13, v11)))
        self.assertTrue(m1.edges.has_key((m1.faces[1].vertices[0], m1.faces[1].vertices[1])))
        self.assertTrue(m1.edges.has_key((m1.faces[1].vertices[1], m1.faces[1].vertices[2])))
        self.assertTrue(m1.edges.has_key((m1.faces[1].vertices[2], m1.faces[1].vertices[0])))

        # check original edges are not present
        self.assertFalse(m1.edges.has_key((v21, v22)))
        self.assertFalse(m1.edges.has_key((v22, v23)))
        self.assertFalse(m1.edges.has_key((v23, v21)))
         
        # check max and min are being calculated correctly
        self.assertTrue(m1.minX==-41)
        self.assertTrue(m1.maxX==40)
        self.assertTrue(m1.minY==-50)
        self.assertTrue(m1.maxY==177)
        self.assertTrue(m1.minZ==-60)
        self.assertTrue(m1.maxZ==100)

if __name__ == '__main__':
    main()

