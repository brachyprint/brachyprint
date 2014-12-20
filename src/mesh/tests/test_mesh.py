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
        self.assertEqual(m.get_vertex(v1), v1)
        self.assertEqual(m.get_vertex(v2), v2)
        self.assertEqual(m.get_vertex(v3), v3)
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

        # check vertices have been cloned
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



class ContainmentTests(TestCase):
    
    def test_cube_contains(self):
        m = Mesh()
        primitives.add_cube(m, 10)
        for (x,y,z) in [(1,2,3), (4,5,6), (7,8,9)]:
            self.assertTrue(m.contains_point(Vector(x,y,z)), "Cube should contain (%d,%d,%d)"%(x,y,z))
        for a in [-1,11]:
            for b in [-1,0,1,9,10,11]:
                for c in [-1,0,1,9,10,11]:
                    for (x,y,z) in [(a,b,c),(a,c,b),(b,a,c),(b,c,a),(c,a,b),(c,b,a)]:
                        self.assertFalse(m.contains_point(Vector(x,y,z)), "Cube should not contain (%d,%d,%d)"%(x,y,z))

    def test_sphere_contains(self):
        m = Mesh()
        primitives.add_sphere(m, 10)
        coords = [-12,-8,-6,-4,-2,2,4,6,8,12]
        for x in coords:
            for y in coords:
                for z in coords:
                    if x*x + y*y + z*z < 100:
                        self.assertTrue(m.contains_point(Vector(x,y,z)), "Sphere should contain point (%f,%f,%f)"%(x,y,z))
                    else:
                        self.assertFalse(m.contains_point(Vector(x,y,z)), "Sphere should not contain point (%f,%f,%f)"%(x,y,z))


class EquivalenceTests(TestCase):
    pass


if __name__ == '__main__':
    main()

