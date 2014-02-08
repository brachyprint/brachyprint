
from __future__ import division

import mesh
from math import pi, cos, sin

import numpy as np
from scipy.spatial import Delaunay

import random


def intersect(m1, m2):
    '''
    Compute the intersection of m1 and m2.

    Returns a new mesh with m2 cut out of m1.
    '''


    # new algorithm:

        # classify vertices in m1 into inside and outside
        # classify vertices in m2 into inside and outside

        # for each face in m1
            # for each face in m2
                # if there is an intersection, record the end points
            # triangulate the m1 face and add extra vertices

        # for each face in m2
            # if intersections are recorded
                # triangulate the m2 face and add extra vertices

        # for each face in m1
            # if all points are outside or on the border
                # add the face to m

        # for each face in m2
            # if all points are inside or on the border
                # add the face to m

    m1_intersections = {}
    m2_intersections = {}

    new_vertices = {}
    new_name = {0: 0} # hack to be visible in the inner function

    m1_vertices = {}
    include_vertex = {}

    # determine if m1 vertex is inside or outside m2
    for v in m1.vertices:
        count = 0
        p = [v, v + mesh.Vector(1, 1, 250)]
        for f2 in m2.faces:

            vs = f2.vertices
            s = mesh.triangle_segment_intersect(p, vs)

            if isinstance(s, mesh.Vector): # XXX: is this correct?
                print s
                count += 1

        if count % 2 == 0: # even number of crossing => outside
            m1_vertices[v.name] = 1
        else:
            m1_vertices[v.name] = 0

    print m1_vertices

    def add_vertex(v, include):
        s = [k for k, ve in new_vertices.iteritems() if ve==v]

        if len(s) == 0:
            new_vertices[new_name[0]] = v
            include_vertex[new_name[0]] = include
            r = new_name[0]
            new_name[0] += 1
        else:
            r = s[0]

        return r
        
    m1_face_points = {}
    for f1 in m1.faces:
        m1_face_points[f1.name] = []

        for i in range(3):
            m1_face_points[f1.name].append(add_vertex(f1.vertices[i], m1_vertices[f1.vertices[i].name]))

    # determine all face/face intersections
    # XXX: optimise this using octrees
    for f1 in m1.faces:

        #f1_vertices[f1.name] = [f1.vertices[0], f1.vertices[1], f1.vertices[2]]
        #for i in range(3):
        #    add_vertex(f1.vertices[i])

        for f2 in m2.faces:

            s = mesh.triangle_triangle_intersect(list(f2.vertices), list(f1.vertices))

            if isinstance(s, list):
                # these two faces intersect
                # add the vertices to the list
                s[0] = add_vertex(s[0], 2)
                s[1] = add_vertex(s[1], 2)

                if f2.name in m2_intersections:
                    m2_intersections[f2.name].append(s)
                else:
                    m2_intersections[f2.name] = [s]

                m1_face_points[f1.name].append(s[0])

                # record edge connections
                if f1.name in m1_intersections:
                    if s[0] in m1_intersections[f1.name]:
                        m1_intersections[f1.name][s[0]].append(s[1])
                    else:
                        m1_intersections[f1.name][s[0]] = [s[1]]
                        
                    if s[1] in m1_intersections[f1.name]:
                        m1_intersections[f1.name][s[1]].append(s[0])
                    else:
                        m1_intersections[f1.name][s[1]] = [s[0]]
                else:
                    m1_intersections[f1.name] = {}
                    m1_intersections[f1.name][s[0]] = [s[1]]
                    m1_intersections[f1.name][s[1]] = [s[0]]

    # create new output mesh
    m = mesh.Mesh()

    #print include_vertex
    # add all the vertices
    nv = []
    for k,v in new_vertices.items():
        if include_vertex[k]:
            nv.append(m.add_vertex(v))
        else:
            print v
            nv.append(None)

    for k,vs in m1_face_points.items():

    #for k,vs in m1_intersections.items():
        # triangulate the face with the new vertices
        
        # fetch all the points in the triangle
        # 3 corners of the original face
        #points = f1_vertices[k]

        # additional vertices
        #vs = [item for sublist in vs for item in sublist]
        #vs = list(set(vs)) # remove duplicates
        #vs = list(vs)

        if len(vs) < 3:
            print "Error!"
        elif len(vs) == 3:
            # no intersection; just add the face
            m.add_face(nv[vs[0]], nv[vs[1]], nv[vs[2]])
            print vs
            print nv[vs[0]]
        else:

            # partition the surface

            edges = [[vs[0]],[vs[1]],[vs[2]]]

            print k
            print m1_intersections[k]
            inter = m1_intersections[k]

            # find the edge points
            edge_points = [k for k,x in m1_intersections[k].items() if len(x)==1]
            print edge_points
            
            bv = [0,0,0]
            bv[0] = new_vertices[vs[1]]-new_vertices[vs[0]]
            bv[1] = new_vertices[vs[2]]-new_vertices[vs[1]]
            bv[2] = new_vertices[vs[0]]-new_vertices[vs[2]]

            # assign each edge point to the corresponding edge
            for p in edge_points:
                for i in range(3):
                    if bv[i].cross(new_vertices[p]-new_vertices[vs[i]]) == mesh.nullVector:
                        edges[i].append(p)
            
            edges = edges[0] + edges[1] + edges[2]

            path = {}
            for p in edge_points:
                # trace out the paths
                ps = [p]
                while 1:
                    for ip in inter[ps[-1]]:
                        if not ip in ps:
                            ps.append(ip)
                    if ps[-1] in edge_points:
                        break
                path[p] = ps[1:]

            partitions = []

            for p in edge_points:
                i = edges.index(p)
                part = [p]
                follow_edge = False
                # traverse round the way
                n = -1
                while n != p:
                    # toggle following the edge, or the partition
                    if n in edge_points:
                        if follow_edge:
                            follow_edge = False
                            i = (i + 1) % len(edges)
                            n = edges[i]
                            part.append(n)
                        else:
                            follow_edge = True
                            for ps in path[n]:
                                if ps == p:
                                    n = p
                                    break
                                else:
                                    part.append(ps)
                            if n == p:
                                continue
                            i = edges.index(part[-1])
                            n = edges[i]
                    else:
                        i = (i + 1) % len(edges)
                        n = edges[i]
                        part.append(n)
                        
                partitions.append(part)
                
            print "partitions"
            print partitions
            print "partitionsend"
                    

            
            for part in partitions:
                if len(part) == 3:
                    # just add the face
                    if include_vertex[part[0]]==2 and include_vertex[part[1]]==2 and include_vertex[part[2]]==2:
                        continue
                    elif include_vertex[part[0]] and include_vertex[part[1]] and include_vertex[part[2]]:
                        m.add_face(nv[part[0]], nv[part[1]], nv[part[2]])
                else:
                    # project the points into a plane for the 2D triangulation
                    
                    vs = part
                    # create orthogonal basis vectors
                    u = new_vertices[vs[1]] - new_vertices[vs[0]]
                    v = new_vertices[vs[1]] - new_vertices[vs[2]]
                    n = v.cross(u)
                    v = n.cross(u)

                    points = []
                    vs = list(set(vs)) # remove duplicates
                    for i in vs:
                        points.append(new_vertices[i] + mesh.Vector(random.uniform(-0.00001, 0.00001), random.uniform(-0.00001, 0.00001), random.uniform(-0.00001, 0.00001)))

                    def dot(a, b):
                        return sum([a[i]*b[i] for i in range(len(a))])

                    def project(a):
                        return [dot(u, a), dot(v, a)]

                    # project every point into 2d
                    for i in range(len(points)):
                        points[i] = project(points[i])

                    # perform the triangulation
                    points = np.array(points)
                    tris = Delaunay(points)

                    try:
                        simplices = tris.simplices
                    except AttributeError: #For compatability with old scipy libraries
                        simplices = tris.vertices
                    for t in simplices:
                        if include_vertex[vs[t[0]]]==2 and include_vertex[vs[t[1]]]==2 and include_vertex[vs[t[2]]]==2:
                            continue
                        elif include_vertex[vs[t[0]]] and include_vertex[vs[t[1]]] and include_vertex[vs[t[2]]]:
                            m.add_face(nv[vs[t[0]]], nv[vs[t[1]]], nv[vs[t[2]]])
                #else:
                #    print vs[t[0]]
                #    print vs[t[1]]
                #    print vs[t[2]]
                #count += 1

    return m


        # coalesce new vertices
        #r = []
        #for i in range(len(vs)-1):
        #    for j in range(i+1, len(vs)):
        #        if vs[i] == vs[j]:
        #            r.append(j)

        #v = []
        #for i in range(len(vs)):
        #    if not i in r:
        #        v.append(vs[i])

        # add new vertices to m1
        



def intersect2(m1, m2):

    interm1 = []; noninterm1 = []
    interm2 = []; noninterm2 = []
    for f2 in m2.faces:
        count = 0
        for f1 in m1.faces:
            # find intersection line
            s = mesh.triangle_triangle_intersect(list(f2.vertices), list(f1.vertices))

            if isinstance(s, mesh.Vector):
                # these two faces intersect
                # add m1 face to interm1
                interm1.append(f1)
        if count > 0:
            # m2 face intersected
            interm2.append(f2)
        else:
            noninterm2.append(f2)


    for f2 in noninterm2:
        # determine if inside or outside m1

        # if all vertices are inside, add face to m
        pass

    for f1 in noninterm1:
        # determine if inside or outside m2

        # if all vertices are outside, add face to m
        pass

    # go through vertices, allocating inside or outside

    outside = []; vertices1 = []

    for f1 in noninterm1:
        for v in f1:

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

            if count > 1:
                print count
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
        elif count == 0 or count == 1 or count == 2: # intersection of two faces
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
                #s2 = mesh.triangle_triangle_intersect(list(f1.vertices), list(f2.vertices))

                #if s != s2:
                    #print s
                    #print s2

                    #print f2.vertices
                    #print f1.vertices
                    #continue

                if isinstance(s, int):
                    continue

            # add f1 to 

                coords1.append((vs1, count2, s, v_other1))

            if count == 0:
                print len(coords1)
            if len(coords1) > 0:
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
            try:
                simplices = tris.simplices
            except AttributeError: #For compatability with old scipy libraries
                simplices = tris.vertices
            for t in simplices:
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

    #m.allocate_volumes()

    return m

