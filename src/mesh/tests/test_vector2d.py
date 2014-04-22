# Unit testing for the Vector2d class

from unittest import TestCase, main

from mesh import *


class BasicArithmeticTests(TestCase):

    def setUp(self):
        self.v1 = Vector2d(1, 2)
        self.v2 = Vector2d(-1, 2)

    def test_add(self):
        # adding two vectors
        v3 = self.v1 + self.v2
        self.assertEqual(v3, Vector2d(0, 4))
        v3 = self.v2 + self.v1
        self.assertEqual(v3, Vector2d(0, 4))

        # adding integer
        with self.assertRaises(NotImplementedError):
            self.v1 + 10

        # adding float
        with self.assertRaises(NotImplementedError):
            self.v1 + 10.1

    def test_sub(self):
        # subtracting two vectors
        v3 = self.v1 - self.v2
        self.assertEqual(v3, Vector2d(2, 0))
        v3 = self.v2 - self.v1
        self.assertEqual(v3, Vector2d(-2, 0))

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
        self.assertEqual(v3, Vector2d(1*2.1, 2*2.1)) # hack

        # ... and rmul
        v3 = 2.1 * self.v1
        self.assertEqual(v3, Vector2d(1*2.1, 2*2.1)) # hack

        # multiplication by int
        v3 = self.v1 * 2
        self.assertEqual(v3, Vector2d(2, 4))

        # ... and rmul
        v3 = 2 * self.v1
        self.assertEqual(v3, Vector2d(2, 4))

        with self.assertRaises(NotImplementedError):
            v3 = self.v1 * self.v2

    def test_div(self):
        # division by float
        v3 = self.v1 / 0.5
        self.assertEqual(v3, Vector2d(2.0, 4.0))

        # division by int
        v3 = self.v1 / 5
        self.assertEqual(v3, Vector2d(0.2, 0.4))

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
        v = Vector2d(1, 2)
        with self.assertRaises(NotImplementedError):
            v += 10

        # infix float addition
        v = Vector2d(1, 2)
        with self.assertRaises(NotImplementedError):
            v += 5.5

        # infix vector addition
        v = Vector2d(1, 2)
        v += Vector2d(1, 3)
        self.assertEqual(v, Vector2d(2, 5))

    def test_infix_sub(self):
        # infix integer subtraction
        v = Vector2d(1, 2)
        with self.assertRaises(NotImplementedError):
            v -= 10

        # infix float subtraction
        v = Vector2d(1, 2)
        with self.assertRaises(NotImplementedError):
            v -= 5.5

        # infix vector subtraction
        v = Vector2d(1, 2)
        v -= Vector2d(1, 3)
        self.assertEqual(v, Vector2d(0, -1))

    def test_infix_mul(self):
        # infix integer multiplication
        v = Vector2d(1, 2)
        v *= 10
        self.assertEqual(v, Vector2d(10, 20))

        # infix float multiplication
        v = Vector2d(1, 2)
        v *= 5.5
        self.assertEqual(v, Vector2d(1*5.5, 2*5.5))

        # infix vector multiplication
        v = Vector2d(1, 2)
        with self.assertRaises(NotImplementedError):
            v *= Vector2d(1, 3)

    def test_infix_div(self):
        # infix integer division
        v = Vector2d(1, 2)
        v /= 10
        self.assertEqual(v, Vector2d(0.1, 0.2))

        # infix float division
        v = Vector2d(1, 2)
        v /= 5.5
        self.assertEqual(v, Vector2d(1.0/5.5, 2.0/5.5))

        # infix vector division
        v = Vector2d(1, 2)
        with self.assertRaises(NotImplementedError):
            v /= Vector2d(1, 3)


class Vector2dManipulationTests(TestCase):

    def setUp(self):
        self.v1 = Vector2d(1, 2)
        self.v2 = Vector2d(-1, 2)
    
    def test_dot_product(self):
        d1 = self.v1.dot(self.v2)
        d2 = self.v2.dot(self.v1)

        self.assertEqual(d1, 3)
        self.assertEqual(d1, d2)

    def test_cross_product(self):
        v1 = self.v1.cross(self.v2)
        v2 = self.v2.cross(self.v1)

        self.assertEqual(v1, 4)
        self.assertEqual(v2, -4)

        v3 = self.v1.cross(self.v1)

        self.assertEqual(v3, 0)

    def test_cross_dot(self):
        v1 = self.v1.cross(self.v2)
        
        # test for AttributeError (2d cross product returns a scalar)
        with self.assertRaises(AttributeError):
            self.assertEqual(v1.dot(self.v1), 0)
        with self.assertRaises(AttributeError):
            self.assertEqual(v1.dot(self.v2), 0)


if __name__ == '__main__':
    main()

