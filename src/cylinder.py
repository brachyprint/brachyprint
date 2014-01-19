
from __future__ import division
import model
from math import pi, cos, sin

def make_cylinder(r, h, sampling):

    c = model.Mesh()

    #create end vertices

    o = c.add_vertex(0,0,0)
    o2 = c.add_vertex(0,0,h)

    vs = []; vs2 = []

    hs=[x*h/10 for x in range(11)]

    for j in range(len(hs)):
        vs.append([])
        for i in range(sampling):
            th = (i+(j%2)*0.5)/sampling*2*pi
            x = r*sin(th)
            y = r*cos(th)
            vs[j].append(c.add_vertex(x,y,hs[j])) #bottom

    
    for j in range(len(vs)-1):
        v = vs[j]
        v2 = vs[j+1]
        for i in range(len(v)):
            c.add_face(v[i],v[i-1],v2[i-1])
            c.add_face(v2[i],v[i],v2[i-1])
            

#        vs2.append(c.add_vertex(x,y,h)) #top

    #create bottom
    for i in range(len(vs[0])):
        c.add_face(vs[0][i-1],vs[0][i],o)

    #create top
    for i in range(len(vs[-1])):
        c.add_face(vs[-1][i],vs[-1][i-1],o2)

    c.allocate_volumes()

    #    c.add_vertex(x,y,h) #top

     #   th2 = (i+1)/sampling*2*pi
      #  x2 = r*sin(th2)
       # y2 = r*cos(th2)
        #c.add_face()
    
    #f=[]

    return c

