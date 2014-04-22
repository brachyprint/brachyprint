
#    Brachyprint -- 3D printing brachytherapy moulds
#    Copyright (C) 2013-14  Martin Green and Oliver Madge
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
A 2D vector class for the ``mesh'' package.
'''

from __future__ import division
from math import sqrt


class Vector2d(object):
    '''
    Class representing a 2D vector.
    '''

    def __init__(self, x, y=None):
        if isinstance(x, tuple) or isinstance(x, list) or isinstance(x, Vector2d):
            y = x[1]
            x = x[0]
    
        self.x, self.y = x, y
        self.epsilon = 0.00001

    def __eq__(self, v):
        if isinstance(v, Vector2d):
            return abs(self.x - v.x) <= self.epsilon and abs(self.y - v.y) <= self.epsilon
        elif isinstance(v, list):
            return abs(self.x - v[0]) <= self.epsilon and abs(self.y - v[1]) <= self.epsilon
        else:
            raise NotImplementedError

    def __ne__(self, v):
        return not self.__eq__(v)

    def __gt__(self, v):
        raise TypeError("Ambiguous meaning for a Vector2d")

    def __lt__(self, v):
        raise TypeError("Ambiguous meaning for a Vector2d")

    def __lshift__(self, other):
        raise TypeError("Vector2d is not a binary type")

    def __rshift__(self, other):
        raise TypeError("Vector2d is not a binary type")

    def __and__(self, other):
        raise TypeError("Vector2d is not a binary type")

    def __xor__(self, other):
        raise TypeError("Vector2d is not a binary type")

    def __or__(self, other):
        raise TypeError("Vector2d is not a binary type")

    def __add__(self, v):
        if isinstance(v, Vector2d):
            return Vector2d(self.x + v.x, self.y + v.y)
        else:
            raise NotImplementedError

    def __neg__(self):
        return Vector2d(-self.x, -self.y)

    def __sub__(self, v):
        if isinstance(v, Vector2d):
            return Vector2d(self.x - v.x, self.y - v.y)
        else:
            raise NotImplementedError

    def __mul__(self, val):
        if isinstance(val, float) or isinstance(val, int):
            return Vector2d(self.x*val, self.y*val)
        else:
            raise NotImplementedError

    def __rmul__(self, other):
        return self.__mul__(other)

    def __div__(self, val):
        if isinstance(val, float) or isinstance(val, int):
            return Vector2d(self.x/val, self.y/val)
        else:
            raise NotImplementedError

    def __truediv__(self, val):
        if isinstance(val, float) or isinstance(val, int):
            return Vector2d(self.x/val, self.y/val)
        else:
            raise NotImplementedError

    def __rtruediv__(self, other):
        return self.__truediv__(other)

    def __iadd__(self, v):
        if isinstance(v, Vector2d):
            self.x += v.x
            self.y += v.y
            return self
        else:
            raise NotImplementedError
        
    def __isub__(self, v):
        if isinstance(v, Vector2d):
            self.x -= v.x
            self.y -= v.y
            return self
        else:
            raise NotImplementedError

    def __imul__(self, val):
        if isinstance(val, float) or isinstance(val, int):
            self.x *= val
            self.y *= val
            return self
        else:
            raise NotImplementedError

    def __getitem__(self, i):
        if i == 0:
            return self.x
        elif i == 1:
            return self.y
        else:
            raise IndexError

    def __len__(self):
        return 2

    def __repr__(self):
        return "<Vector2d x:%f y:%f z:%f>" % (self.x, self.y)

    def __str__(self):
        return "From str method of Vector2d: x is %f, y is %f" % (self.x, self.y)

    def cross(self, v):
        return self.x*v.y - self.y*v.x

    def dot(self, v):
        return self.x * v.x + self.y * v.y

    def magnitude(self):
        return sqrt(self.x ** 2 + self.y ** 2)

    def normalise(self):
        m = self.magnitude()
        if m == 0.0:
            return Vector2d(self.x, self.y)
        else:
            return Vector2d(self.x/m, self.y/m)

    def get_orthogonal_vectors(self):
        '''
        Returns two orthogonal vectors
        '''
        for bv in BASIS_VECTORS:
            p = self.cross(bv)
            if p.magnitude() > 0.1:
                return p.normalise(), self.cross(p).normalise()

#BASIS_VECTORS = [Vector(0,0,1), Vector(0,1,0), Vector(1,0,0)]
nullVector2d = Vector2d(0, 0)

