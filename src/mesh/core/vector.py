
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
A 3D vector class for the ``mesh'' package.
'''

from __future__ import division
from math import sqrt


class Vector(object):
    '''
    Class representing a vector.
    '''

    def __init__(self, x, y=None, z=None):
        if isinstance(x, tuple) or isinstance(x, list) or isinstance(x, Vector):
            y = x[1]
            z = x[2]
            x = x[0]
    
        self.x, self.y, self.z = x, y, z
        self.epsilon = 0.00001

    def __eq__(self, v):
        if isinstance(v, Vector):
            return abs(self.x - v.x) <= self.epsilon and abs(self.y - v.y) <= self.epsilon and abs(self.z - v.z) <= self.epsilon
        elif isinstance(v, list):
            return abs(self.x - v[0]) <= self.epsilon and abs(self.y - v[1]) <= self.epsilon and abs(self.z - v[2]) <= self.epsilon
        else:
            raise NotImplementedError

    def __ne__(self, v):
        return not self.__eq__(v)

    def __gt__(self, v):
        raise TypeError("Ambiguous meaning for a Vector")

    def __lt__(self, v):
        raise TypeError("Ambiguous meaning for a Vector")

    def __lshift__(self, other):
        raise TypeError("Vector is not a binary type")

    def __rshift__(self, other):
        raise TypeError("Vector is not a binary type")

    def __and__(self, other):
        raise TypeError("Vector is not a binary type")

    def __xor__(self, other):
        raise TypeError("Vector is not a binary type")

    def __or__(self, other):
        raise TypeError("Vector is not a binary type")

    def __add__(self, v):
        if isinstance(v, Vector):
            return Vector(self.x + v.x, self.y + v.y, self.z + v.z)
        else:
            raise NotImplementedError

    def __neg__(self):
        return Vector(-self.x, -self.y, -self.z)

    def __sub__(self, v):
        if isinstance(v, Vector):
            return Vector(self.x - v.x, self.y - v.y, self.z - v.z)
        else:
            raise NotImplementedError

    def __mul__(self, val):
        if isinstance(val, float) or isinstance(val, int):
            return Vector(self.x*val, self.y*val, self.z*val)
        else:
            raise NotImplementedError

    def __rmul__(self, other):
        return self.__mul__(other)

    def __div__(self, val):
        if isinstance(val, float) or isinstance(val, int):
            return Vector(self.x/val, self.y/val, self.z/val)
        else:
            raise NotImplementedError

    def __truediv__(self, val):
        if isinstance(val, float) or isinstance(val, int):
            return Vector(self.x/val, self.y/val, self.z/val)
        else:
            raise NotImplementedError

    def __rtruediv__(self, other):
        return self.__truediv__(other)

    def __iadd__(self, v):
        if isinstance(v, Vector):
            self.x += v.x
            self.y += v.y
            self.z += v.z
            return self
        else:
            raise NotImplementedError
        
    def __isub__(self, v):
        if isinstance(v, Vector):
            self.x -= v.x
            self.y -= v.y
            self.z -= v.z
            return self
        else:
            raise NotImplementedError

    def __imul__(self, val):
        if isinstance(val, float) or isinstance(val, int):
            self.x *= val
            self.y *= val
            self.z *= val
            return self
        else:
            raise NotImplementedError

    def __getitem__(self, i):
        if i == 0:
            return self.x
        elif i == 1:
            return self.y
        elif i == 2:
            return self.z
        else:
            raise IndexError

    def __len__(self):
        return 3

    def __repr__(self):
        return "<Vector x:%f y:%f z:%f>" % (self.x, self.y, self.z)

    def __str__(self):
        return "From str method of Vector: x is %f, y is %f, z is %f" % (self.x, self.y, self.z)

    def cross(self, v):
        return Vector(self.y * v.z - self.z * v.y,
                      self.z * v.x - self.x * v.z,
                      self.x * v.y - self.y * v.x)

    def dot(self, v):
        return self.x * v.x + self.y * v.y + self.z * v.z

    def magnitude(self):
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalise(self):
        m = self.magnitude()
        if m == 0.0:
            return Vector(self.x, self.y, self.z)
        else:
            return Vector(self.x/m, self.y/m, self.z/m)

    def project2d(self, u, v):
        '''
        Project the vector into 2d using the basis vectors 'u' and 'v'.
        '''
        return [self.dot(u), self.dot(v)]


nullVector = Vector(0, 0, 0)

