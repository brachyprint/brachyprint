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

# Unit testing for the Polygon class

from unittest import TestCase, main

from mesh import *

import itertools


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

    def test_create_from_list(self):
        vs = [Vector2d(0,0),
              Vector2d(0,1),
              Vector2d(1,0)]
        ls = [(0,1),(1,2),(2,0)]
        p = Polygon((vs, ls))

        self.assertEqual(len(p.vertices), 3)
        self.assertEqual(len(p.lines), 3)
        self.assertTrue(p.closed())

    def test_split_lines(self):
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

        v4 = p.add_vertex(0,0.5)

        self.assertEqual(len(p.vertices), 4)
        self.assertEqual(len(p.lines), 4)
        self.assertTrue(p.closed())
        

class PartitionPolygonTests(TestCase):

    def setUp(self):
        pass

    def rotations(self, paths):
        """Generate the set of rotations (forward and reversed) of a list.
        
        Also converts lists to tuples (a hashable type).
        """
        paths_rotated = []
        for i, path in enumerate(paths):
            x = itertools.cycle(path)
            forward = [tuple([x.next() for i in range(len(path)+1)][0:-1]) for j in path]
            #y = itertools.cycle(reversed(path))
            #backward = [tuple([y.next() for i in range(len(path)+1)][0:-1]) for j in path]

            #paths_rotated.append(set(forward + backward))
            paths_rotated.append(set(forward))
        return paths_rotated

    def checkPaths(self, paths, paths_valid):
        """Check that every path returned is valid.
        """
        used_paths = [False] * len(paths_valid)
        for path in paths:
            p = tuple(map(lambda x: x.name, path))
            ret = [j for j, valid in enumerate(paths_valid) if p in valid]
            self.assertEqual(len(ret), 1)
            used_paths[ret[0]] = True

        # check that every path was returned
        self.assertTrue(sum(used_paths)==len(paths_valid))

    def check_partition(self, p, paths_expected):
        """Check the partition agrees with the expected paths.
        """
        paths_valid = self.rotations(paths_expected)

        # partition polygon
        paths = p.partition()
        
        # check the correct number of paths were returned
        self.assertEqual(len(paths), len(paths_expected))

        self.checkPaths(paths, paths_valid)

    def test_simple_partition(self):
        p = Polygon()

        v1 = p.add_vertex(1,2)
        v2 = p.add_vertex(0,1)
        v3 = p.add_vertex(2,1)
        v4 = p.add_vertex(0,0)
        v5 = p.add_vertex(2,0)

        # region 1
        p.add_line(v1, v2)
        p.add_line(v2, v3)
        p.add_line(v3, v1)

        # region 2
        p.add_line(v5, v3)
        p.add_line(v4, v5)
        p.add_line(v2, v4)

        self.assertEqual(len(p.vertices), 5)
        self.assertEqual(len(p.lines), 6)
        self.assertTrue(p.closed())

        paths = p.partition()
        self.assertEqual(len(paths), 2)
        
        # flatten all the vertices from the various paths
        path_vertices = [v for path in paths for v in path]
        for v in p.vertices:
            # count the number of occurrences of `v' in path_vertices
            count = len([v_t for v_t in path_vertices if v_t==v])
            # assert that the count is equal to the number of lines leaving that vertex, less 1
            self.assertEqual(len(v.lines)-1, count)

    def test_triangle_partition_1(self):
        # simple triangle:
        #     1
        #     ^
        #    / \
        #   /___\ 
        #  0     2

        vertices = [Vector2d(1,1),
                    Vector2d(6,6),
                    Vector2d(11,1)]
        lines = [(0,1),(1,2),(2,0)]
        paths_expected = [[0, 2, 1]]

        p = Polygon((vertices, lines))
        self.check_partition(p, paths_expected)

    def test_triangle_partition_2(self):
        # triangle with partition on one edge:
        #      1
        #      ^
        #     / \
        #    / 4 \
        #   /  ^  \
        #  /__/_\__\ 
        # 0  5   3  2

        vertices = [Vector2d(1,1),
                    Vector2d(6,6),
                    Vector2d(11,1),
                    Vector2d(8,1),
                    Vector2d(6,4),
                    Vector2d(4,1)]
        lines = [(0,1),(1,2),(2,3),(3,5),(5,0),(3,4),(4,5)]
        paths_expected = [[0, 5, 4, 3, 2, 1], [5, 3, 4]]

        p = Polygon((vertices, lines))
        self.check_partition(p, paths_expected)

    def test_triangle_partition_3(self):
        # triangle with partition spanning two edges
        #      2
        #      ^
        #    1/ \
        #    /\  \
        #   /  \5 \
        #  /___/___\ 
        # 0   4     3

        vertices = [Vector2d(1,1),
                    Vector2d(3,3),
                    Vector2d(6,6),
                    Vector2d(11,1),
                    Vector2d(4,1),
                    Vector2d(6,4)]
        lines = [(0,1),(1,2),(2,3),(3,4),(4,0),(4,5),(5,1)]
        paths_expected = [[0, 4, 5, 1], [1, 5, 4, 3, 2]]

        p = Polygon((vertices, lines))
        self.check_partition(p, paths_expected)

    def test_triangle_partition_4(self):
        # triangle with three partitions connecting all three edges
        #       2
        #       ^
        #     1/ \
        #     /\  \3
        #    /  \/ \
        #   /   /6  \
        #  /___/_____\ 
        # 0   5       4

        vertices = [Vector2d(1,1),
                    Vector2d(3,3),
                    Vector2d(6,6),
                    Vector2d(9,3),
                    Vector2d(11,1),
                    Vector2d(4,1),
                    Vector2d(6,4)]
        lines = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,0),(1,6),(3,6),(5,6)]
        paths_expected = [[0, 5, 6, 1], [1, 6, 3, 2], [3, 6, 5, 4]]

        p = Polygon((vertices, lines))
        self.check_partition(p, paths_expected)

    def test_rectangle_partition(self):
        # rectangle with two partitions
        #
        # 1___________2
        #  |         |
        #  |         |
        # 4|_________|5
        #  |         |
        #  |         |
        # 0|_________|3

        p = Polygon()

        v0 = p.add_vertex(1,1)
        v1 = p.add_vertex(1,5)
        v2 = p.add_vertex(5,5)
        v3 = p.add_vertex(5,1)

        # original rectangle
        p.add_line(v0, v1)
        p.add_line(v1, v2)
        p.add_line(v2, v3)
        p.add_line(v3, v0)

        # add two additional vertices and a line to form a partition
        v4 = p.add_vertex(1,3)
        v5 = p.add_vertex(5,3)

        # dividing line
        p.add_line(v5, v4)

        paths_expected = [[0, 3, 5, 4], [1, 4, 5, 2]]

        self.check_partition(p, paths_expected)


if __name__ == '__main__':
    main()

