# Unit testing for the Vector class

from unittest import TestCase, main

from mesh import *


class BasicArithmeticTests(TestCase):

    def setUp(self):
        self.v1 = Vector(1, 2, 3)
        self.v2 = Vector(-1, 2, 4)

    def test_add(self):
        # adding two vectors
        v3 = self.v1 + self.v2
        self.assertEqual(v3, Vector(0, 4, 7))
        v3 = self.v2 + self.v1
        self.assertEqual(v3, Vector(0, 4, 7))

        # adding integer
        with self.assertRaises(NotImplementedError):
            self.v1 + 10

        # adding float
        with self.assertRaises(NotImplementedError):
            self.v1 + 10.1

    def test_sub(self):
        # subtracting two vectors
        v3 = self.v1 - self.v2
        self.assertEqual(v3, Vector(2, 0, -1))
        v3 = self.v2 - self.v1
        self.assertEqual(v3, Vector(-2, 0, 1))

        # subtracting integer
        with self.assertRaises(NotImplementedError):
            self.v1 - 10

        # subtracting float
        with self.assertRaises(NotImplementedError):
            self.v1 - 10.1

    def test_mul(self):
        # multiplication by float
        # XXX: needs some thought due to floating point rounding
        v3 = self.v1 * 2.1
        self.assertEqual(v3, Vector(1*2.1, 2*2.1, 3*2.1)) # hack

        # ... and rmul
        v3 = 2.1 * self.v1
        self.assertEqual(v3, Vector(1*2.1, 2*2.1, 3*2.1)) # hack

        # multiplication by int
        v3 = self.v1 * 2
        self.assertEqual(v3, Vector(2, 4, 6))

        # ... and rmul
        v3 = 2 * self.v1
        self.assertEqual(v3, Vector(2, 4, 6))

        with self.assertRaises(NotImplementedError):
            v3 = self.v1 * self.v2

    def test_div(self):
        # division by float
        v3 = self.v1 / 0.5
        self.assertEqual(v3, Vector(2.0, 4.0, 6.0))

        # division by int
        v3 = self.v1 / 5
        self.assertEqual(v3, Vector(0.2, 0.4, 0.6))

        #division of int by vector
        with self.assertRaises(TypeError):
            v3 = 5 / self.v1

        #division of float by vector
        with self.assertRaises(TypeError):
            v3 = 0.5 / self.v1

        # division of two vectors
        with self.assertRaises(NotImplementedError):
            v3 = self.v1 / self.v2

    def test_no_binary(self):
        # right shift
        with self.assertRaises(TypeError):
            self.v1 >> 1

        # left shift
        with self.assertRaises(TypeError):
            self.v1 << 1

        # left shift
        with self.assertRaises(TypeError):
            self.v1 << 1

        # binary and
        with self.assertRaises(TypeError):
            self.v1 & self.v2

        # binary xor
        with self.assertRaises(TypeError):
            self.v1 ^ self.v2

        # binary or
        with self.assertRaises(TypeError):
            self.v1 | self.v2

    def test_infix_add(self):
        # infix integer addition
        v = Vector(1, 2, 3)
        with self.assertRaises(NotImplementedError):
            v += 10

        # infix float addition
        v = Vector(1, 2, 3)
        with self.assertRaises(NotImplementedError):
            v += 5.5

        # infix vector addition
        v = Vector(1, 2, 3)
        v += Vector(1, 3, 5)
        self.assertEqual(v, Vector(2, 5, 8))

    def test_infix_sub(self):
        # infix integer subtraction
        v = Vector(1, 2, 3)
        with self.assertRaises(NotImplementedError):
            v -= 10

        # infix float subtraction
        v = Vector(1, 2, 3)
        with self.assertRaises(NotImplementedError):
            v -= 5.5

        # infix vector subtraction
        v = Vector(1, 2, 3)
        v -= Vector(1, 3, 5)
        self.assertEqual(v, Vector(0, -1, -2))

    def test_infix_mul(self):
        # infix integer multiplication
        v = Vector(1, 2, 3)
        v *= 10
        self.assertEqual(v, Vector(10, 20, 30))

        # infix float multiplication
        v = Vector(1, 2, 3)
        v *= 5.5
        self.assertEqual(v, Vector(1*5.5, 2*5.5, 3*5.5))

        # infix vector multiplication
        v = Vector(1, 2, 3)
        with self.assertRaises(NotImplementedError):
            v *= Vector(1, 3, 5)

    def test_infix_div(self):
        # infix integer division
        v = Vector(1, 2, 3)
        v /= 10
        self.assertEqual(v, Vector(0.1, 0.2, 0.3))

        # infix float division
        v = Vector(1, 2, 3)
        v /= 5.5
        self.assertEqual(v, Vector(1.0/5.5, 2.0/5.5, 3.0/5.5))

        # infix vector division
        v = Vector(1, 2, 3)
        with self.assertRaises(NotImplementedError):
            v /= Vector(1, 3, 5)


class VectorManipulationTests(TestCase):

    def setUp(self):
        self.v1 = Vector(1, 2, 3)
        self.v2 = Vector(-1, 2, 4)
    
    def test_dot_product(self):
        d1 = self.v1.dot(self.v2)
        d2 = self.v2.dot(self.v1)

        self.assertEqual(d1, 15)
        self.assertEqual(d1, d2)

    def test_cross_product(self):
        v1 = self.v1.cross(self.v2)
        v2 = self.v2.cross(self.v1)

        self.assertEqual(v1, Vector(2, -7, 4))
        self.assertEqual(v2, Vector(-2, 7, -4))

        v3 = self.v1.cross(self.v1)

        self.assertEqual(v3, nullVector)

    def test_cross_dot(self):
        v1 = self.v1.cross(self.v2)
        
        # test for orthogonality
        self.assertEqual(v1.dot(self.v1), 0)
        self.assertEqual(v1.dot(self.v2), 0)

class PerpendicularVectorTests(TestCase):

    def test_get_orthogonal_vectors(self):
        vs = [Vector(1, 2, 3), Vector(-1, 2, 4)]
        for v in vs:
            a, b = v.get_orthogonal_vectors()
            self.assertAlmostEqual(v.dot(a), 0)
            self.assertAlmostEqual(v.dot(b), 0)
            self.assertAlmostEqual(a.dot(b), 0)
            self.assertAlmostEqual(a.magnitude(), 1)
            self.assertAlmostEqual(b.magnitude(), 1)


if __name__ == '__main__':
    main()

