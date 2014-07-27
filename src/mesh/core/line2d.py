
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


'''
A 2D line class for the ``mesh'' package.
'''

from __future__ import division

from mesh_settings import epsilon

class Line(object):
    '''
    A class representing a 2D line segment.
    '''

    def __init__(self, name, v1, v2):
        self.name = name
        self.v1, self.v2 = v1, v2

    def __repr__(self):
        return "Line from %d to %d" % (self.v1.name, self.v2.name)
        #return "Line from %s to %s" % (self.v1.__repr__(), self.v2.__repr__())

    def length(self):
        """Returns the length of the line segment.
        """
        return (self.v2 - self.v1).magnitude()

    def contains(self, v):
        """Returns True if the vector `v' lies on the line.
        """
        try:
            tx = (v.x - self.v1.x)/(self.v2.x - self.v1.x)
        except ZeroDivisionError:
            if v.x != self.v1.x: # vertical line, but x coordinate doesn't match
                return False
            tx = None
        try:
            ty = (v.y - self.v1.y)/(self.v2.y - self.v1.y)
        except ZeroDivisionError:
            if v.y != self.v1.y: # horizontal line, but y coordinate doesn't match
                return False
            ty = None

        if tx is None:
            t = ty
        elif ty is None:
            t = tx
        elif abs(tx - ty) > epsilon:
            return False
        else:
            t = tx

        if t <= 0 or t >= 1: # outside the line segment
            return False

        return True

    def to_ratio(self, v):
        """
        (Assuming v lies on this edge), how far of the way along does
        it lie? Calling this on v1 yields 0.0, and calling it on v2
        yields 1.0.
        """
        d = self.displacement()
        return (v-self.v1).dot(d) / d.magnitude()

    def from_ratio(self, i):
        """
        Return a vector i of the way from v1 to v2.
        """
        return self.v2*i + self.v1*(1-i)

