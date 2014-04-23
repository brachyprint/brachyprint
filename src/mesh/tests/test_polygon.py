# Unit testing for the Mesh class

from unittest import TestCase, main

from mesh import *


class BasicPolygonTests(TestCase):

    def setUp(self):
        pass

    def test_create(self):
        p = Polygon()

        v1 = p.add_vertex(0,0)
        v2 = p.add_vertex(0,1)
        v3 = p.add_vertex(1,0)

        p.add_line(v1, v2)
        p.add_line(v2, v3)
        p.add_line(v3, v1)

        self.assertEqual(len(p.vertices), 3)

        self.assertEqual(len(p.lines), 3)

        self.assertTrue(p.closed())

class PartitionPolygonTests(TestCase):

    def setUp(self):
        pass

    def test_simple_partition(self):
        p = Polygon()

        v1 = p.add_vertex(1,2)
        v2 = p.add_vertex(0,1)
        v3 = p.add_vertex(2,1)
        v4 = p.add_vertex(0,0)
        v5 = p.add_vertex(2,0)

        p.add_line(v1, v2)
        p.add_line(v2, v3)
        p.add_line(v3, v1)

        p.add_line(v5, v3)
        p.add_line(v4, v5)
        p.add_line(v2, v4)

        self.assertEqual(len(p.vertices), 5)
        self.assertEqual(len(p.lines), 6)
        self.assertTrue(p.closed())

        paths = p.partition()
        self.assertEqual(len(paths), 3)
        
        path_vertices = [v for path in paths for v in path]
        for v in p.vertices:
            count = len([v_t for v_t in path_vertices if v_t==v])
            self.assertEqual(len(v.lines), count)


if __name__ == '__main__':
    main()

