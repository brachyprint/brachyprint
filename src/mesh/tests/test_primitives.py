"""Unit testing for the mesh primitives class
"""

from __future__ import division

from unittest import TestCase, main

from math import pi, sin, sqrt

import mesh


class PrimitiveTests(TestCase):

    def assertAlmostEqualVector(self,u,v):
        self.assertAlmostEqual(u.x,v.x)
        self.assertAlmostEqual(u.y,v.y)
        self.assertAlmostEqual(u.z,v.z)

    def test_cube_closed(self):
        m = mesh.Mesh()
        mesh.primitives.add_cube(m, 100)
        self.assertTrue(m.closed())

    def test_octrahedron_closed(self):
        m = mesh.Mesh()
        mesh.primitives.add_sphere(m, 1.0, model="octa")
        self.assertTrue(m.closed())

    def test_cylinder_closed(self):
        m = mesh.Mesh()
        mesh.primitives.add_cylinder(m, 10, 100, 100)
        self.assertTrue(m.closed())

    def test_sphere_closed(self):
        m = mesh.Mesh()
        mesh.primitives.add_sphere(m, 1.0)
        self.assertTrue(m.closed())

    def test_torus_closed(self):
        m = mesh.Mesh()
        mesh.primitives.add_torus(m, 3, 1, 100, 100)
        self.assertTrue(m.closed())

    def test_something_not_closed(self):
        m = mesh.Mesh()
        v1 = m.add_vertex(0, 0, 0)
        v2 = m.add_vertex(10, 0, 0)
        v3 = m.add_vertex(0, 10, 0)
        m.add_face(v1, v2, v3)
        self.assertFalse(m.closed())

    def expected_cube_volume(self,l):
        return l**3

    def test_cube1_volume(self):
        m = mesh.Mesh()
        l = 100
        mesh.primitives.add_cube(m, l)
        self.assertAlmostEqual(m.volume(), self.expected_cube_volume(l))

    def test_cube2_volume(self):
        m = mesh.Mesh()
        l = 100
        o = [10, 20, 99]
        mesh.primitives.add_cube(m, l, o)
        self.assertAlmostEqual(m.volume(), self.expected_cube_volume(l))

    def expected_cylinder_volume(self,r,h,n):
        return 0.5*r*r*sin(2*pi/n)*n*h

    def test_cylinder_volumes(self):
        for (r,h,n) in [(10,100,100),(10,100,250)]:
            m = mesh.Mesh()
            mesh.primitives.add_cylinder(m,r,h,n)
            self.assertAlmostEqual(m.volume(), self.expected_cylinder_volume(r,h,n))

    def expected_sphere_volume(self,r):
        return 4/3 * pi * r**3

    def expected_octahedron_volume(self,r):
        return 4/3 * r**3

    def test_octahedron_volume(self):
        m = mesh.Mesh()
        r = 0.8
        mesh.primitives.add_sphere(m, r, model="octa", detail_level=1)
        self.assertAlmostEqual(m.volume(), self.expected_octahedron_volume(r))

    def expected_icosahedron_volume(self,r):
        return 5/12 * (3 + sqrt(5)) * (r * 4 / sqrt(10 + 2 * sqrt(5)))**3

    def test_icosahedron_volume(self):
        m = mesh.Mesh()
        r = 1
        mesh.primitives.add_sphere(m, r, detail_level=1)
        self.assertAlmostEqual(m.volume(), self.expected_icosahedron_volume(r))

    def test_sphere_volume(self):
        r = 0.8
        for model in ["icosa","octa"]:
            m = mesh.Mesh()
            mesh.primitives.add_sphere(m, r, model=model, detail_level=25)
            self.assertAlmostEqual(m.volume(), self.expected_sphere_volume(r), places=1)

    def test_cube_centroids(self):
        m = mesh.Mesh()
        mesh.primitives.add_cube(m, 100)
        centroid0 = mesh.Vector(50.0,50.0,50.0)
        centroid1 = m.solid_centroid()
        centroid2 = m.surface_centroid()
        self.assertAlmostEqualVector(centroid1, centroid0)
        self.assertAlmostEqualVector(centroid2, centroid0)
  
    def test_cylinder_centroids(self):
        for (r,h,n) in [(10,100,50)]:
            m = mesh.Mesh()
            mesh.primitives.add_cylinder(m, r, h, n)
            v = mesh.Vector(0,0,h/2)
            self.assertAlmostEqualVector(m.solid_centroid(), v)
            self.assertAlmostEqualVector(m.surface_centroid(), v)

    def test_sphere_centroids(self):
        m = mesh.Mesh()
        v = mesh.Vector(23,45,67)
        mesh.primitives.add_sphere(m,2.0,origin=v,model="octa",detail_level=3)
        self.assertAlmostEqualVector(m.solid_centroid(), v)
        self.assertAlmostEqualVector(m.surface_centroid(), v)

    def test_torus_centroids(self):
        m = mesh.Mesh()
        v = mesh.Vector(1,2,3)
        mesh.primitives.add_torus(m, 3, 1, 20, 20, offset=v)
        self.assertAlmostEqualVector(m.solid_centroid(), v)
        self.assertAlmostEqualVector(m.surface_centroid(), v)

    def test_cube_area(self):
        m = mesh.Mesh()
        mesh.primitives.add_cube(m, 100)
        area = 100.0*100.0*6
        self.assertAlmostEqual(m.surface_area(), area)

    def expected_cylinder_area(self,r,h,n):
        return r*r*sin(2*pi/n)*n + 2*r*sin(pi/n)*n*h

    def test_cylinder1_area(self):
        m = mesh.Mesh()
        r,h,n = 10,100,4
        mesh.primitives.add_cylinder(m, r, h, n)
        self.assertAlmostEqual(m.surface_area(), self.expected_cylinder_area(r,h,n))

    def test_cylinder2_area(self):
        m = mesh.Mesh()
        r,h,n = 10,100,100
        mesh.primitives.add_cylinder(m, r, h, n)
        self.assertAlmostEqual(m.surface_area(), self.expected_cylinder_area(r,h,n))

    def expected_octahedron_area(self,r):
        return 4*sqrt(3)*r**2

    def test_octahedron_area(self):
        m = mesh.Mesh()
        r = 0.8
        mesh.primitives.add_sphere(m, r, model="octa", detail_level=1)
        self.assertAlmostEqual(m.surface_area(), self.expected_octahedron_area(r))

    def expected_icosahedron_area(self,r):
        # XXX: can this be simplified?
        return 5*sqrt(3)*(r * 4 / sqrt(10 + 2*sqrt(5)))**2

    def test_icosahedron_area(self):
        m = mesh.Mesh()
        r = 0.9
        mesh.primitives.add_sphere(m, r, model="icosa", detail_level=1)
        self.assertAlmostEqual(m.surface_area(), self.expected_icosahedron_area(r))

if __name__ == '__main__':
    main()

