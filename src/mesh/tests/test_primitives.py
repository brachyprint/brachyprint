"""Unit testing for the Vector class
"""

from __future__ import division

from unittest import TestCase, main

from math import pi, sin, sqrt

import mesh

class SizeTests(TestCase):

    def setUp(self):
        pass

    def test_primitive_closed(self):
        m = mesh.Mesh()
        mesh.primitives.make_cube(m, 100)
        self.assertTrue(m.closed())

        m.clear()
        mesh.primitives.make_cylinder(m, 10, 100, 100)
        self.assertTrue(m.closed())

        m.clear()
        mesh.primitives.add_sphere(m, 1.0)
        self.assertTrue(m.closed())

        m.clear()
        v1 = m.add_vertex(0, 0, 0)
        v2 = m.add_vertex(10, 0, 0)
        v3 = m.add_vertex(0, 10, 0)
        m.add_face(v1, v2, v3)
        self.assertFalse(m.closed())
    

    def test_primitive_volume(self):
        m = mesh.Mesh()
        mesh.primitives.make_cube(m, 100)
        volume = 100.0*100.0*100.0
        self.assertAlmostEqual(m.volume(), volume)

        m.clear()
        mesh.primitives.make_cube(m, 100, [10, 20, 99])
        volume = 100.0*100.0*100.0
        self.assertAlmostEqual(m.volume(), volume)

        m.clear()
        mesh.primitives.make_cylinder(m, 10, 100, 100)
        volume = 0.5*10.0*10.0*sin(2.0*pi/100.0)*100.0*100.0
        self.assertAlmostEqual(m.volume(), volume)

        m.clear()
        mesh.primitives.make_cylinder(m, 10, 100, 10000)
        volume = 0.5*10.0*10.0*sin(2.0*pi/10000.0)*10000.0*100.0
        self.assertAlmostEqual(m.volume(), volume)

        m.clear()
        mesh.primitives.add_sphere(m, 1.0, detail_level=1)

        e = m.edges.itervalues().next()

        volume = sqrt(2)/3*(e.v2-e.v1).magnitude()**3
        self.assertAlmostEqual(volume, m.volume())

        m.clear()
        mesh.primitives.add_sphere(m, 1.0, detail_level=2)
        e = m.edges.itervalues().next()
        # XXX: this should really be calculated
        volume = 2.942809041582063

        self.assertAlmostEqual(volume, m.volume())


    def test_primitive_area(self):
        m = mesh.Mesh()
        mesh.primitives.make_cube(m, 100)
        area = 100.0*100.0*6
        self.assertAlmostEqual(m.surface_area(), area)

        m.clear()
        s = 4.0
        mesh.primitives.make_cylinder(m, 10, 100, int(s))
        area = 0.5*10.0*10.0*sin(2.0*pi/s)*s*2.0 + 2.0*10.0*sin(2.0*pi/s/2.0)*s*100.0
        self.assertAlmostEqual(m.surface_area(), area)

        m.clear()
        s = 100.0
        mesh.primitives.make_cylinder(m, 10, 100, int(s))
        area = 0.5*10.0*10.0*sin(2.0*pi/s)*s*2.0 + 2.0*10.0*sin(2.0*pi/s/2.0)*s*100.0
        self.assertAlmostEqual(m.surface_area(), area)


if __name__ == '__main__':
    main()

