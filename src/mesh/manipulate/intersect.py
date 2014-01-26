
from __future__ import division

import mesh
from math import pi, cos, sin

import numpy as np
from scipy.spatial import Delaunay


def intersect(m1, m2):
    '''
    Compute the intersection of m1 and m2.

    Returns a new mesh with m2 cut out of m1.
    '''

    m = mesh.Mesh()
    
    p = [[],[]]
    fs = []

    # go through vertices, allocating inside or outside

    outside = []; vertices1 = []

    for v in m1.vertices:

        #n = p[0].faces[0].normal
        p[0] = v.tovector()
        count = 0
        for f in m2.faces:
            vs = f.vertices

            # construct a vector in a arbitrary direction to represent the line segment
            # XXX: ensure this always extends outside object
            p[1] = p[0] + mesh.Vector(0, 0, 150)

            s = mesh.triangle_segment_intersect(p, vs)


            if isinstance(s, int) and s == 2:
                print "umph"

            if isinstance(s, mesh.Vector): # XXX: is this correct?
                count += 1

        if count % 2 == 0: # m1 vertex is outside m2 (even number of intersections)
            #m.add_vertex(p[0][0], p[0][1], p[0][2])
            #print "%f %f %f %f %f %f" %(p[0][0], p[0][1], p[0][2], n[0], n[1], n[2])
            #count2 += 1

            outside.append(v.name)
            v = v.tovector()
            vertices1.append(m.add_vertex(v[0], v[1], v[2]))

    # go through faces, relate back to vertices
    for f1 in m1.faces:
        count = 0

        vs = []
        for v in f1.vertices:
            if v.name in outside:
                count += 1
                vs.append(vertices1[outside.index(v.name)])

        if count == 3: # all outside
            m.add_face(*vs)


    inside = []; vertices = []

    for v in m2.vertices:
        #n = p[0].faces[0].normal
        p[0] = v.tovector()
        count = 0
        for f in m1.faces:
            vs = f.vertices

            p[1] = p[0] + mesh.Vector(0, 0, 150)

            s = mesh.triangle_segment_intersect(p, vs)

            if isinstance(s, int) and s == 2:
                print "umph2"

            if isinstance(s, mesh.Vector):
                count += 1

        if count % 2 == 1: # m2 vertex is inside m1 (odd number of intersections)
            #print "%f %f %f %f %f %f" %(p[0][0], p[0][1], p[0][2], n[0], n[1], n[2])
            #count2 += 1

            inside.append(v.name)
            v = v.tovector()
            vertices.append(m.add_vertex(v[0], v[1], v[2]))

    f2s = []
    # go through faces, relate back to vertices
    for f2 in m2.faces:
        count = 0

        vs2 = []
        v_other2 = []
        for v in f2.vertices:
            if v.name in inside:
                count += 1
                vs2.append(vertices[inside.index(v.name)])
            else:
                v_other2.append(v)

        if count == 3: # all inside
            m.add_face(vs2[0], vs2[2], vs2[1])
            #m.add_face(*f2.vertices)
        elif count == 1 or count == 2: # intersection of two faces
            # search through m1 faces to find intersection
            coords1 = []
            for f1 in m1.faces:
                vs1 = []
                v_other1 = []
                count2 = 0

                # check if this face is inside or outside
                for v in f1.vertices:
                    if v.name in outside:
                        count2 += 1
                        vs1.append(vertices1[outside.index(v.name)])
                    else:
                        v_other1.append(v)

                if count2 == 3:
                    continue

                # find intersection line
                s = mesh.triangle_triangle_intersect(list(f2.vertices), list(f1.vertices))
                s2 = mesh.triangle_triangle_intersect(list(f1.vertices), list(f2.vertices))

                if s != s2:
                    print s
                    print s2

                    print f2.vertices
                    print f1.vertices
                #    continue

                if isinstance(s, int):
                    continue

            # add f1 to 

                coords1.append((vs1, count2, s, v_other1))

            f2s.append((vs2, coords1, count, v_other2))


    for f in f2s:
        vs2 = f[0]
        coords1 = f[1]
        v_other2 = f[3]
        if f[2] == 1:
            for c in coords1:
                s = c[2]
                v0 = m.add_vertex(s[0][0], s[0][1], s[0][2])
                v1 = m.add_vertex(s[1][0], s[1][1], s[1][2])

                m.add_face(v0, v1, vs2[0])

                #vs1 = c[0]
                #if c[1] == 1:
                #    m.add_face(v0, v1, vs1[0])
        elif f[2] == 2:
            # create a new vertex at the intersection between (vs2[0], vs2[1])
            # and (s[0], v_other2[0])
            if len(coords1) == 0:
                continue
            s = coords1[0][2]
            #v0 = m.add_vertex(s[0][0], s[0][1], s[0][2])
            #v1 = m.add_vertex(s[1][0], s[1][1], s[1][2])
            #m.add_face(v0, v1, vs2[0])
            #m.add_face(vs2[0], v1, vs2[1])
            #for c in coords1[1:]:
                #s = c[2]

                #v0 = v1
                #v1 = m.add_vertex(s[1][0], s[1][1], s[1][2])
                #m.add_face(vs2[0], v1, vs2[1])
                #m.add_face(v0, v1, vs2[1])

            u = vs2[1].tovector() - vs2[0].tovector()
            v = vs2[1].tovector() - s[0]
            n = v.cross(u)
            v = n.cross(u)

            def dot(a, b):
                return sum([a[i]*b[i] for i in range(len(a))])

            def project(a):
                return [dot(u, a), dot(v, a)]

            points = [project([vs2[0].x, vs2[0].y, vs2[0].z]), project([vs2[1].x, vs2[1].y, vs2[1].z])]

            s = coords1[0][2]
            p = []
            p.append(m.add_vertex(vs2[0].x, vs2[0].y, vs2[0].z))
            p.append(m.add_vertex(vs2[1].x, vs2[1].y, vs2[1].z))

            points.append(project([s[0][0], s[0][1], s[0][2]]))
            p.append(m.add_vertex(s[0][0], s[0][1], s[0][2]))
            for c in coords1:
                s = c[2]
                points.append(project([s[1][0], s[1][1], s[1][2]]))
                p.append(m.add_vertex(s[1][0], s[1][1], s[1][2]))
            points = np.array(points)
            tris = Delaunay(points)

            for t in tris.simplices:
                m.add_face(p[t[0]], p[t[1]], p[t[2]])
                

        elif 0:
            p_prev = vs2[0]

            if len(coords1) > 1:
                p = mesh.line_intersect(vs2, [s[0], v_other2[0]])
                p_new = m.add_vertex(p[0], p[1], p[2])

                s = coords1[0][2]
                v0 = m.add_vertex(s[0][0], s[0][1], s[0][2])
                v1 = m.add_vertex(s[1][0], s[1][1], s[1][2])
                for c in coords1[1:-1]:
                    m.add_face(v1, p_prev, v0)
                    m.add_face(p_new, p_prev, v1)

                    p_prev = p_new
                    p = mesh.line_intersect(vs2, [s[0], v_other2[0]])
                    p_new = m.add_vertex(p[0], p[1], p[2])
                    v0 = v1
                    s = c[2]
                    v1 = m.add_vertex(s[1][0], s[1][1], s[1][2])


    if 0:
        # create a new face
        if count == 1: # 1 vertex of f2 is inside
            v0 = m.add_vertex(s[0][0], s[0][1], s[0][2])
            v1 = m.add_vertex(s[1][0], s[1][1], s[1][2])
            #m.add_face(v0, v1, vs2[0])

            if count2 == 1:
                #m.add_face(v0, v1, vs1[0]) 
                pass
            elif count2 == 2:
                m.add_face(v0, vs1[0], v1)
                m.add_face(vs1[0], vs1[1], v1)

            # create a single triangle between s[0], s[1] and vs[0]
        if count == 2: # 2 vertices of f2 are inside
            v0 = m.add_vertex(s[0][0], s[0][1], s[0][2])
            v1 = m.add_vertex(s[1][0], s[1][1], s[1][2])
            #m.add_face(v1, vs2[0], v0)
            #m.add_face(vs2[1], vs2[0], v1)
            # create two faces between (s[0], s[1], vs[0]) and (s[0], s[1], vs[1])
            # XXX: might require more faces ideally

            if count2 == 1:
                #m.add_face(v0, v1, vs1[0]) 
                pass
            elif count2 == 2:
                m.add_face(v0, vs1[0], v1)
                m.add_face(vs1[0], vs1[1], v1)

    m.allocate_volumes()

    return m

