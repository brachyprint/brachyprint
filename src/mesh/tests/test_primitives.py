"""Unit testing for the Vector class
"""

from unittest import TestCase, main
from math import pi, sin

import mesh

class BasicArithmeticTests(TestCase):

    def setUp(self):
        pass

    def test_volume(self):
        m = mesh.Mesh()
        mesh.primitives.make_cube(m, 100)
        self.assertAlmostEqual(m.volume(), 1000000.0)

        m.clear()
        mesh.primitives.make_cube(m, 100, [10, 20, 99])
        self.assertAlmostEqual(m.volume(), 1000000.0)

        m.clear()
        mesh.primitives.make_cylinder(m, 10, 100, 100)
        volume = 0.5*10.0*10.0*sin(2.0*pi/100.0)*100.0*100.0
        self.assertAlmostEqual(m.volume(), volume)

        m.clear()
        mesh.primitives.make_cylinder(m, 10, 100, 10000)
        volume = 0.5*10.0*10.0*sin(2.0*pi/10000.0)*10000.0*100.0
        self.assertAlmostEqual(m.volume(), volume)

if __name__ == '__main__':
    main()

