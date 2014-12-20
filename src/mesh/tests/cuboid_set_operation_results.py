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

def intersection_volume(((ax1, ax2), (ay1, ay2), (az1, az2)), 
                        ((bx1, bx2), (by1, by2), (bz1, bz2))):
    if ax1 > ax2: ax1, ax2 = ax2, ax1    
    if ay1 > ay2: ay1, ay2 = ay2, ay1
    if az1 > az2: az1, az2 = az2, az1
    if bx1 > bx2: bx1, bx2 = bx2, bx1    
    if by1 > by2: by1, by2 = by2, by1
    if bz1 > bz2: bz1, bz2 = bz2, bz1    
    dx = min(ax2, bx2) - max(ax1, bx1)   
    dy = min(ay2, by2) - max(ay1, by1)   
    dz = min(az2, bz2) - max(az1, bz1)
    if dx < 0 or dy < 0 or dz < 0:
        return 0
    else:
        return dx * dy * dz

def difference_volume(((ax1, ax2), (ay1, ay2), (az1, az2)), 
                      ((bx1, bx2), (by1, by2), (bz1, bz2))):
    if ax1 > ax2: ax1, ax2 = ax2, ax1    
    if ay1 > ay2: ay1, ay2 = ay2, ay1
    if az1 > az2: az1, az2 = az2, az1 
    return (ax2 - ax1) * (ay2 - ay1) * (az2 - az1) - \
           intersection_volume(((ax1, ax2), (ay1, ay2), (az1, az2)), 
                               ((bx1, bx2), (by1, by2), (bz1, bz2)))
    
