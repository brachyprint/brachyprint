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
Unit testing for intersection of two cuboids

(C) Martin Green 2014
"""

from unittest import TestCase, skip
from mesh.primitives import add_cuboid
from mesh import Vector, Mesh
from mesh.manipulate.intersect4 import intersect, union
from cuboid_set_operation_results import intersection_volume, union_volume

class IntersectionTests(TestCase):
    def test_intersection_no_intersect(self):
        self.check_intersection(((0, 1), (0, 1), (0, 1)), 
                                ((2, 3), (0, 1), (0, 1)), 0)
    def test_intersection_vertex_intersect(self):
        self.check_intersection(((0, 1), (0, 1), (0, 1)), 
                                ((1, 2), (1, 2), (1, 2)), 0)
    def test_intersection_edge_intersect(self):
        self.check_intersection(((0, 1), (0, 1), (0, 1)), 
                                ((1, 2), (0, 1), (1, 2)), 0)
    def test_intersection_face_intersect(self):
        self.check_intersection(((0, 1), (0, 1), (0, 1)), 
                                ((1, 2), (0, 1), (0, 1)), 0)
    def test_union_no_intersect(self):
        self.check_union(((0, 1), (0, 1), (0, 1)), 
                         ((2, 3), (0, 1), (0, 1)), 16)
                         
    def test_union_vertex_intersection(self):
        self.check_union(((0, 1), (0, 1), (0, 1)), 
                         ((1, 2), (1, 2), (1, 2)), 15)
                         
    def test_union_edge_intersection(self):
        self.check_union(((0, 1), (0, 1), (0, 1)), 
                         ((1, 2), (0, 1), (1, 2)), 15) #Edge will be split and hence extra vertex
                         
    def test_union_face_intersection(self):
        self.check_union(((0, 1), (0, 1), (0, 1)), 
                         ((1, 2), (0, 1), (0, 1)), 17) #Edges will be split and hence extra 5 verticies
        
    def intersection(self, 
                     ((ax1, ax2), (ay1, ay2), (az1, az2)), 
                     ((bx1, bx2), (by1, by2), (bz1, bz2))):
        ma = Mesh()
        add_cuboid(ma, corner = Vector(ax1, ay1, az1), lx = ax2 - ax1, ly = ay2 - ay1, lz = az2 - az1)
        mb = Mesh()
        add_cuboid(mb, corner = Vector(bx1, by1, bz1), lx = bx2 - bx1, ly = by2 - by1, lz = bz2 - bz1)
        mi = intersect(ma, mb)
        return mi
        
       
    def union(self, 
              ((ax1, ax2), (ay1, ay2), (az1, az2)), 
              ((bx1, bx2), (by1, by2), (bz1, bz2))):
        ma = Mesh()
        add_cuboid(ma, corner = Vector(ax1, ay1, az1), lx = ax2 - ax1, ly = ay2 - ay1, lz = az2 - az1)
        mb = Mesh()
        add_cuboid(mb, corner = Vector(bx1, by1, bz1), lx = bx2 - bx1, ly = by2 - by1, lz = bz2 - bz1)
        mi = union(ma, mb)
        return mi
        
    def check_intersection(self, 
                           ((ax1, ax2), (ay1, ay2), (az1, az2)), 
                           ((bx1, bx2), (by1, by2), (bz1, bz2)),
                           excepted_number_of_verticies):
        mi = self.intersection(((ax1, ax2), (ay1, ay2), (az1, az2)), 
                               ((bx1, bx2), (by1, by2), (bz1, bz2)))
        self.assertAlmostEqual(mi.volume(), 
                               intersection_volume(((ax1, ax2), (ay1, ay2), (az1, az2)), 
                                                   ((bx1, bx2), (by1, by2), (bz1, bz2))))
        self.assertEqual(len(mi.vertices), excepted_number_of_verticies)
        
    def check_union(self, 
                    ((ax1, ax2), (ay1, ay2), (az1, az2)), 
                    ((bx1, bx2), (by1, by2), (bz1, bz2)),
                    excepted_number_of_verticies):
        mi = self.union(((ax1, ax2), (ay1, ay2), (az1, az2)), 
                        ((bx1, bx2), (by1, by2), (bz1, bz2)))
        self.assertAlmostEqual(mi.volume(), 
                               union_volume(((ax1, ax2), (ay1, ay2), (az1, az2)), 
                                            ((bx1, bx2), (by1, by2), (bz1, bz2))))
        self.assertEqual(len(mi.vertices), excepted_number_of_verticies)
