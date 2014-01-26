
from __future__ import division

import mesh
from math import pi, cos, sin

def make_cylinder(c, r, h, sampling, offset=[0,0,0]):
    '''
    Add a cylinder to an existing mesh.
    '''

    # create end vertices

    o = c.add_vertex(offset[0],offset[1],offset[2])
    o2 = c.add_vertex(offset[0],offset[1],h+offset[2])

    vs = []; vs2 = []

    hs=[x*h/10 + offset[2] for x in range(11)]

    for j in range(len(hs)):
        vs.append([])
        for i in range(sampling):
            th = (i+(j%2)*0.5)/sampling*2*pi
            x = r*sin(th) + offset[0]
            y = r*cos(th) + offset[1]
            vs[j].append(c.add_vertex(x,y,hs[j])) # bottom

    
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

    c.allocate_volumes()

    return c


