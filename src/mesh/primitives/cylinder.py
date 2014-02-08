
from __future__ import division

import mesh
from math import pi, cos, sin

def cross(a, b):
    c = [a[1]*b[2] - a[2]*b[1],
         a[2]*b[0] - a[0]*b[2],
         a[0]*b[1] - a[1]*b[0]]
    return c

def dot(a, b):
    return sum([x * y for x, y in zip(a, b)])

def normalise(a):
    magnitude = sum([x ** 2 for x in a]) ** 0.5
    return [x / magnitude for x in a]

class transform_and_add_vertex:
    def __init__(self, mesh, offset, axis, perp1, perp2):
        self.mesh = mesh
        self.offset = offset
        self.axis = axis
        self.perp1 = perp1
        self.perp2 = perp2
    def __call__(self, x, y, z):
        return self.mesh.add_vertex(*[o + x * p1 + y * p2 + z * a 
                                      for o, p1, p2, a 
                                      in zip(self.offset, self.perp1, self.perp2, self.axis)])
def make_cylinder(c, r, h, sampling, axis=[0, 0, 1], offset=[0,0,0]):
    '''
    Add a cylinder of radius r and height h to the existing mesh c.
    '''

    #Find a normalised orthogonal set of vectors
    axis = normalise(axis)
    for arbitary_vector in [[0, 0, 1], [0, 1, 0], [1, 0, 0]]:
        if dot(arbitary_vector, axis) < 0.6:  #One of the above vectors dot producted with a normalised vector must be less than 1/3 ** 1/2
            perp1 = normalise(cross(arbitary_vector, axis))
            perp2 = normalise(cross(axis, perp1))
            break
    add_vertex = transform_and_add_vertex(c, offset, axis, perp1, perp2)
    # create end vertices

    o = add_vertex(0, 0, 0)
    o2 = add_vertex(0, 0, h)

    vs = []; vs2 = []

    #hs=[x*h/10 for x in range(11)]
    hs=[x*h/2 for x in range(3)]

    for j in range(len(hs)):
        vs.append([])
        for i in range(sampling):
            th = (i+(j%2)*0.5)/sampling*2*pi
            x = r*sin(th)
            y = r*cos(th)
            vs[j].append(add_vertex(x,y,hs[j])) # bottom

    
    for j in range(len(vs)-1):
        v = vs[j]
        v2 = vs[j+1]
        for i in range(len(v)):
            c.add_face(v[i],v[i-1],v2[i-1])
            c.add_face(v2[i],v[i],v2[i-1])
            
    # create bottom
    for i in range(len(vs[0])):
        c.add_face(vs[0][i-1],vs[0][i],o)

    # create top
    for i in range(len(vs[-1])):
        c.add_face(vs[-1][i],vs[-1][i-1],o2)

    return c 

