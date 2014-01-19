import unittest
import points
import numpy

class TestMakePoints(unittest.TestCase):

    def setUp(self): 
        self.seq = range(10)

    def test_simpleZ(self):
        t = numpy.array([[[0, 0], [0, 0]], [[1000, 1000], [1000, 1000]]])
        zpositions = [0, 1]
        posX = 0
        posY = 0
        spacingX = 1 
        spacingY = 1 
        r = points.makepoints(t, zpositions, posX, posY, spacingX, spacingY, 500)
        self.assertEqual(r, '0.500000 0.500000 0.500000 0.000000 0.000000 1.000000\n')

    def test_simpleY(self):
        t = numpy.array([[[0, 0], [1000, 1000]], [[0, 0], [1000, 1000]]])
        zpositions = [0, 1]
        posX = 0
        posY = 0
        spacingX = 1 
        spacingY = 1 
        r = points.makepoints(t, zpositions, posX, posY, spacingX, spacingY, 500)
        self.assertEqual(r, '0.500000 0.500000 0.500000 0.000000 1.000000 0.000000\n')

    def test_simpleX(self):
        t = numpy.array([[[0, 1000], [0, 1000]], [[0, 1000], [0, 1000]]])
        zpositions = [0, 1]
        posX = 0
        posY = 0
        spacingX = 1 
        spacingY = 1 
        r = points.makepoints(t, zpositions, posX, posY, spacingX, spacingY, 500)
        self.assertEqual(r, '0.500000 0.500000 0.500000 1.000000 0.000000 0.000000\n')

    def test_simpleoffsetZ(self):
        t = numpy.array([[[100, 100], [100, 100]], [[1100, 1100], [1100, 1100]]])
        zpositions = [0, 1]
        posX = 0
        posY = 0
        spacingX = 1 
        spacingY = 1 
        r = points.makepoints(t, zpositions, posX, posY, spacingX, spacingY, 500)
        self.assertEqual(r, '0.500000 0.500000 0.400000 0.000000 0.000000 1.000000\n')

    def test_simpleoffsetY(self):
        t = numpy.array([[[100, 100], [1100, 1100]], [[100, 100], [1100, 1100]]])
        zpositions = [0, 1]
        posX = 0
        posY = 0
        spacingX = 1 
        spacingY = 1 
        r = points.makepoints(t, zpositions, posX, posY, spacingX, spacingY, 500)
        self.assertEqual(r, '0.500000 0.400000 0.500000 0.000000 1.000000 0.000000\n')

    def test_simpleoffsetX(self):
        t = numpy.array([[[100, 1100], [100, 1100]], [[100, 1100], [100, 1100]]])
        zpositions = [0, 1]
        posX = 0
        posY = 0
        spacingX = 1 
        spacingY = 1 
        r = points.makepoints(t, zpositions, posX, posY, spacingX, spacingY, 500)
        self.assertEqual(r, '0.400000 0.500000 0.500000 1.000000 0.000000 0.000000\n')

    def test_simpleoffsetZ2(self):
        t = numpy.array([[[100, 100], [100, 100]], [[1100, 1100], [1100, 1100]]])
        zpositions = [0, 0.1]
        posX = 0
        posY = 0
        spacingX = 0.1 
        spacingY = 0.1 
        r = points.makepoints(t, zpositions, posX, posY, spacingX, spacingY, 500)
        self.assertEqual(r, '0.050000 0.050000 0.040000 0.000000 0.000000 0.100000\n')

    def test_simpleoffsetY2(self):
        t = numpy.array([[[100, 100], [1100, 1100]], [[100, 100], [1100, 1100]]])
        zpositions = [0, 0.1]
        posX = 0
        posY = 0
        spacingX = 0.1 
        spacingY = 0.1 
        r = points.makepoints(t, zpositions, posX, posY, spacingX, spacingY, 500)
        self.assertEqual(r, '0.050000 0.040000 0.050000 0.000000 0.100000 0.000000\n')

    def test_simpleoffsetX2(self):
        t = numpy.array([[[100, 1100], [100, 1100]], [[100, 1100], [100, 1100]]])
        zpositions = [0, 0.1]
        posX = 0
        posY = 0
        spacingX = 0.1 
        spacingY = 0.1 
        r = points.makepoints(t, zpositions, posX, posY, spacingX, spacingY, 500)
        self.assertEqual(r, '0.040000 0.050000 0.050000 0.100000 0.000000 0.000000\n')

    def test_notonsurface(self):
        t = numpy.array([[[100, 1100], [100, 1100]], [[100, 1100], [100, 1100]]])
        zpositions = [0, 1]
        posX = 0
        posY = 0
        spacingX = 1 
        spacingY = 1 
        r = points.makepoints(t, zpositions, posX, posY, spacingX, spacingY, 1200)
        self.assertEqual(r, '')


    def test_positions_and_spacings(self):
        t = numpy.array([[[0, 1000], [0, 1000]], [[0, 1000], [0, 1000]]])
        zpositions = [40, 50]
        posX = 40
        posY = 40
        spacingX = 30 
        spacingY = 30 
        r = points.makepoints(t, zpositions, posX, posY, spacingX, spacingY, 500)
        self.assertEqual(r, '55.000000 55.000000 45.000000 30.000000 0.000000 0.000000\n')

    def test_positions_and_spacings(self):
        t = numpy.array([[[0, 500], [500, 1000]], [[500, 1000], [1000, 1500]]])
        zpositions = [40, 50]
        posX = 50
        posY = 60
        spacingX = 10 
        spacingY = 10 
        r = points.makepoints(t, zpositions, posX, posY, spacingX, spacingY, 750)
        self.assertEqual(r, '55.000000 65.000000 45.000000 5.773503 5.773503 5.773503\n')


if __name__ == '__main__':
    unittest.main()
