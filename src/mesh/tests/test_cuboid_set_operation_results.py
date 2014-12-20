#    Copyright (C) 2014  Martin Green
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

"""
Unit testing for determining paramters of the intersections of two cuboids

(C) Martin Green 2014
"""
from unittest import TestCase, skip
from cuboid_set_operation_results import *

class IntersectionVolumesTests(TestCase):
    def test_complete_intersection(self):
        self.assertAlmostEqual(intersection_volume(((0, 1), (0, 1), (0, 1)), 
                                                   ((0, 1), (0, 1), (0, 1))),
                         1)
        self.assertAlmostEqual(intersection_volume(((4, 5), (-9, -11), (1.5, 1)), 
                                                   ((4, 5), (-9, -11), (1.5, 1))),
                         1)
    def test_no_intersection(self):
        self.assertAlmostEqual(intersection_volume(((0, 1), (0, 1), (0, 1)), 
                                                   ((1, 2), (0, 1), (0, 1))),
                         0)
        self.assertAlmostEqual(intersection_volume(((0, 1), (0, 1), (0, 1)), 
                                                   ((0, 1), (1, 2), (0, 1))),
                         0)
        self.assertAlmostEqual(intersection_volume(((0, 1), (0, 1), (0, 1)), 
                                                   ((0, 1), (0, 1), (1, 2))),
                         0)
    def test_internal_intersection(self):
        self.assertAlmostEqual(intersection_volume(((0, 1), (0, 1), (0, 1)), 
                                                   ((-1, 2), (-1, 2), (-1, 2))),
                         1)
        self.assertAlmostEqual(intersection_volume(((-1, 2), (-1, 2), (-1, 2)), 
                                                   ((0, 1), (0, 1), (0, 1))),
                         1)
    def test_overlap_intersection(self):
        self.assertAlmostEqual(intersection_volume(((0, 1), (0, 1), (0, 1)), 
                                                   ((0.5, 2), (0, 1), (0, 1))),
                         0.5)
        self.assertAlmostEqual(intersection_volume(((0, 1), (0, 1), (0, 1)), 
                                                   ((0, 1), (0.5, 2), (0, 1))),
                         0.5)
        self.assertAlmostEqual(intersection_volume(((0, 1), (0, 1), (0, 1)), 
                                                   ((0, 1), (0, 1), (0.5, 2))),
                         0.5)
        self.assertAlmostEqual(intersection_volume(((0.5, 2), (0, 1), (0, 1)), 
                                                   ((0, 1), (0, 1), (0, 1))),
                         0.5)
        self.assertAlmostEqual(intersection_volume(((0, 1), (0.5, 2), (0, 1)), 
                                                   ((0, 1), (0, 1), (0, 1))),
                         0.5)
        self.assertAlmostEqual(intersection_volume(((0, 1), (0, 1), (0.5, 2)), 
                                                   ((0, 1), (0, 1), (0, 1))),
                         0.5)

class DifferenceVolumesTests(TestCase):
    def test_complete_difference(self):
        self.assertAlmostEqual(difference_volume(((0, 1), (0, 1), (0, 1)), 
                                                   ((0, 1), (0, 1), (0, 1))),
                         0)
        self.assertAlmostEqual(difference_volume(((4, 5), (-9, -11), (1.5, 1)), 
                                                  ((4, 5), (-9, -11), (1.5, 1))),
                         0)
    def test_no_difference(self):
        self.assertAlmostEqual(difference_volume(((0, 1), (0, 1), (0, 1)), 
                                                 ((1, 2), (0, 1), (0, 1))),
                         1)
        self.assertAlmostEqual(difference_volume(((0, 1), (0, 1), (0, 1)), 
                                                   ((0, 1), (1, 2), (0, 1))),
                         1)
        self.assertAlmostEqual(difference_volume(((0, 1), (0, 1), (0, 1)), 
                                                   ((0, 1), (0, 1), (1, 2))),
                         1)
    def test_internal_difference(self):
        self.assertAlmostEqual(difference_volume(((0, 1), (0, 1), (0, 1)), 
                                                 ((-1, 2), (-1, 2), (-1, 2))),
                         0)
        self.assertAlmostEqual(difference_volume(((-1, 2), (-1, 2), (-1, 2)), 
                                                   ((0, 1), (0, 1), (0, 1))),
                         26)
    def test_overlap_difference(self):
        self.assertAlmostEqual(difference_volume(((0, 1), (0, 1), (0, 1)), 
                                                 ((0.5, 2), (0, 1), (0, 1))),
                         0.5)
        self.assertAlmostEqual(difference_volume(((0, 1), (0, 1), (0, 1)), 
                                                 ((0, 1), (0.5, 2), (0, 1))),
                         0.5)
        self.assertAlmostEqual(difference_volume(((0, 1), (0, 1), (0, 1)), 
                                                 ((0, 1), (0, 1), (0.5, 2))),
                         0.5)
        self.assertAlmostEqual(difference_volume(((0.5, 2), (0, 1), (0, 1)), 
                                                 ((0, 1), (0, 1), (0, 1))),
                         1)
        self.assertAlmostEqual(difference_volume(((0, 1), (0.5, 2), (0, 1)), 
                                                 ((0, 1), (0, 1), (0, 1))),
                         1)
        self.assertAlmostEqual(difference_volume(((0, 1), (0, 1), (0.5, 2)), 
                                                 ((0, 1), (0, 1), (0, 1))),
                         1)
