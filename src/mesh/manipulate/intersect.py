
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

        # classify vertices in m1 into inside and outside m2
        # classify vertices in m2 into inside and outside m1

        # for each face in m1
            # for each face in m2
                # if there is an intersection, record the end points
            # partition and triangulate the m1 face and add extra vertices

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
    m2_vertices = {}
    include_vertex = {}

    # determine if m1 vertex is inside or outside m2
    for v in m1.vertices:
        count = 0
        p = [v, v + mesh.Vector(1, 1, 250)]
        for f2 in m2.faces:

            vs = f2.vertices
            s = mesh.triangle_segment_intersect(p, vs)

            if isinstance(s, mesh.Vector): # XXX: is this correct?
                count += 1

        if count % 2 == 0: # even number of crossing => outside
            m1_vertices[v.name] = 1
        else:
            m1_vertices[v.name] = 0

    # determine if m2 vertex is inside or outside m1
    for v in m2.vertices:
        count = 0
        p = [v, v + mesh.Vector(1, 1, 250)]
        for f1 in m1.faces:

            vs = f1.vertices
            s = mesh.triangle_segment_intersect(p, vs)

            if isinstance(s, mesh.Vector): # XXX: is this correct?
                count += 1

        if count % 2 == 0: # even number of crossing => outside
            m2_vertices[v.name] = 0
        else:
            m2_vertices[v.name] = 1

    # add vertices to the new vertex list, reusing existing vertices
    # if extant
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

    m2_face_points = {}
    for f2 in m2.faces:
        m2_face_points[f2.name] = []

        for i in range(3):
            m2_face_points[f2.name].append(add_vertex(f2.vertices[i], m2_vertices[f2.vertices[i].name]))

    # determine all face/face intersections
    # XXX: optimise this using octrees
    for f1 in m1.faces:

        for f2 in m2.faces:

            s = mesh.triangle_triangle_intersect(list(f2.vertices), list(f1.vertices))

            if isinstance(s, list):
                # these two faces intersect
                # add the vertices to the list

                s[0] = add_vertex(s[0], 2)
                s[1] = add_vertex(s[1], 2)

                #if f2.name in m2_intersections:
                #    m2_intersections[f2.name].append(s)
                #else:
                #    m2_intersections[f2.name] = [s]

                if not s[0] in m1_face_points[f1.name]:
                    m1_face_points[f1.name].append(s[0])
                if not s[1] in m1_face_points[f1.name]:
                    m1_face_points[f1.name].append(s[1])

                # record m1 edge connections
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

                # record m2 vertices
                if not s[0] in m2_face_points[f2.name]:
                    m2_face_points[f2.name].append(s[0])
                if not s[1] in m2_face_points[f2.name]:
                    m2_face_points[f2.name].append(s[1])

                # record m2 edge connections
                if f2.name in m2_intersections:
                    if s[0] in m2_intersections[f2.name]:
                        m2_intersections[f2.name][s[0]].append(s[1])
                    else:
                        m2_intersections[f2.name][s[0]] = [s[1]]
                        
                    if s[1] in m2_intersections[f2.name]:
                        m2_intersections[f2.name][s[1]].append(s[0])
                    else:
                        m2_intersections[f2.name][s[1]] = [s[0]]
                else:
                    m2_intersections[f2.name] = {}
                    m2_intersections[f2.name][s[0]] = [s[1]]
                    m2_intersections[f2.name][s[1]] = [s[0]]

    # create new output mesh
    m = mesh.Mesh()

    # add all the vertices
    nv = []
    for k,v in new_vertices.items():
        if include_vertex[k]:
            nv.append(m.add_vertex(v))
        else:
            nv.append(None)

    output_faces(m1_face_points, include_vertex, m1_intersections, new_vertices, m, nv)
    output_faces(m2_face_points, include_vertex, m2_intersections, new_vertices, m, nv, True)

    return m


def output_faces(face_points, include_vertex, intersections, new_vertices, m, nv, invert=False):

    # output the faces from m1
    for k,vs in face_points.items():

        # triangulate the face with the new vertices

        if len(vs) < 3:
            print "Error!"
        elif len(vs) == 3:
            # no intersection; just add the face
            if include_vertex[vs[0]] and include_vertex[vs[1]] and include_vertex[vs[2]]:
                if invert:
                    m.add_face(nv[vs[1]], nv[vs[0]], nv[vs[2]])
                else:
                    m.add_face(nv[vs[0]], nv[vs[1]], nv[vs[2]])
        else:

            # partition the surface

            edges = [[vs[0]],[vs[1]],[vs[2]]]

            inter = intersections[k]

            # find the edge points
            edge_points = [ki for ki,x in intersections[k].items() if len(x)==1]
            #print edge_points
            #print "len vs", len(vs)
            #print vs
            
            bv = [0,0,0]
            bv[0] = new_vertices[vs[1]]-new_vertices[vs[0]]
            bv[1] = new_vertices[vs[2]]-new_vertices[vs[1]]
            bv[2] = new_vertices[vs[0]]-new_vertices[vs[2]]

            # assign each edge point to the corresponding edge
            # XXX: are you sure this always puts them in the correct order?
            for p in edge_points:
                for i in range(3):
                    if bv[i].cross(new_vertices[p]-new_vertices[vs[i]]) == mesh.nullVector:
                        edges[i].append(p)
            
            edges = edges[0] + edges[1] + edges[2]

            #if len(edge_points)+3 != len(edges):
            #    print "Not enough edge points!"
            #    continue

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
                
            #print "partitions"
            #print partitions
            #print "partitionsend"
                    

            
            for part in partitions:
                if len(part) == 3:
                    # just add the face
                    if not invert and include_vertex[part[0]]==2 and include_vertex[part[1]]==2 and include_vertex[part[2]]==2:
                        continue
                    elif include_vertex[part[0]] and include_vertex[part[1]] and include_vertex[part[2]]:
                        if invert:
                            m.add_face(nv[part[1]], nv[part[0]], nv[part[2]])
                        else:
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
                    #vs = list(set(vs)) # remove duplicates
                    for i in vs:
                        #points.append(new_vertices[i] + mesh.Vector(random.uniform(-0.00001, 0.00001), random.uniform(-0.00001, 0.00001), random.uniform(-0.00001, 0.00001)))
                        points.append(new_vertices[i])

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
                        if not invert and include_vertex[vs[t[0]]]==2 and include_vertex[vs[t[1]]]==2 and include_vertex[vs[t[2]]]==2:
                            continue
                        elif include_vertex[vs[t[0]]] and include_vertex[vs[t[1]]] and include_vertex[vs[t[2]]]:
                            if invert:
                                m.add_face(nv[vs[t[0]]], nv[vs[t[1]]], nv[vs[t[2]]])
                            else:
                                m.add_face(nv[vs[t[1]]], nv[vs[t[0]]], nv[vs[t[2]]])




