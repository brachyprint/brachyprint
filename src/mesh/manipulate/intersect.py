
from __future__ import division

import mesh

from random import uniform


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
        # XXX: this is going to break at some point! Fix with octrees
        p = [v, v.normal() + mesh.Vector(uniform(-0.1, 0.1), uniform(-0.1, 0.1), uniform(-0.1, 0.1))]
        for f2 in m2.faces:

            vs = f2.vertices
            s = mesh.triangle_segment_intersect(p, vs, 1)

            if isinstance(s, mesh.Vector):
                count += 1

        if count % 2 == 0: # even number of crossing => outside
            m1_vertices[v.name] = 1
        else:
            m1_vertices[v.name] = 0

    # determine if m2 vertex is inside or outside m1
    for v in m2.vertices:
        count = 0
        # XXX: this is going to break at some point! Fix with octrees
        p = [v, v.normal() + mesh.Vector(uniform(-0.1, 0.1), uniform(-0.1, 0.1), uniform(-0.1, 0.1))]
        for f1 in m1.faces:

            vs = f1.vertices
            s = mesh.triangle_segment_intersect(p, vs, 1)

            if isinstance(s, mesh.Vector):
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
        elif len(s) > 1:
            raise ValueError("Should be at most 1 point")
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

                # record m1 vertices
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
            
            bv = [0,0,0]
            bv[0] = new_vertices[vs[1]]-new_vertices[vs[0]]
            bv[1] = new_vertices[vs[2]]-new_vertices[vs[1]]
            bv[2] = new_vertices[vs[0]]-new_vertices[vs[2]]

            #map(lambda x: print(edge_points[x]), range(len(edge_points)))
            #for i in range(len(edge_points)):
            #    print edge_points[i], nv[edge_points[i]]
            
            # assign each edge point to the corresponding edge
            for p in edge_points:
                for i in range(3):
                    #print bv[i].cross(new_vertices[p]-new_vertices[vs[i]])
                    if bv[i].cross(new_vertices[p]-new_vertices[vs[i]]) == mesh.nullVector:
                        edges[i].append(p)

            for j in range(3):
                edges[j] = [(bv[j].dot(new_vertices[edges[j][i]]), edges[j][i]) for i in range(len(edges[j]))]
                edges[j].sort(key=lambda t: t[0])
                edges[j] = [edges[j][i][1] for i in range(len(edges[j]))]
            
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

            #print inter
            #print edges
            #print edge_points

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

            # cull any duplicate partitions
            partition_sets = range(len(partitions))

            for i in range(len(partitions)):
                partition_sets[i] = set(partitions[i])

            to_delete = []
            for i in range(len(partition_sets)):
                for j in range(len(partition_sets)):
                    if i==j or partition_sets[i] == None or partition_sets[j] == None:
                        continue
                    if partition_sets[i] == partition_sets[j]:
                        partition_sets[j] = None
                        to_delete.append(j)

            # delete in reverse order so as not to disturb the indices
            to_delete.sort(reverse=True)

            for i in to_delete:
                del partitions[i]
                
            # work out which partitions to display
            # start at v[0], if in include_vertex, display that partition.
            # find all partitions adjacent to v[0] partition
                # set display opposite to v[0] partition
            # find all partitions adjacent to these partitions
                # set display the same as v[0] partition
            # etc.

            ps_i = range(len(partitions))
            disp = [None]*len(partitions)

            for p in ps_i:
                if vs[0] in partitions[p]:
                    disp[p] = (include_vertex[vs[0]] == 1)
                    part_prev = p
                    break

            def find_all_adj(p_prev):
                for p in ps_i:
                    if disp[p] != None:
                        continue
                    # must share an edge (i.e. two points)
                    if len([i for i in partitions[p] if i in partitions[p_prev]]) > 1:
                        disp[p] = not disp[p_prev]
                        find_all_adj(p)

            find_all_adj(part_prev)

            # XXX: check that the display of partitions containing v[1] and v[2]
            # are set correctly according to include_vertex
            for p in ps_i:
                if vs[1] in partitions[p]:
                    if disp[p] != (include_vertex[vs[1]] == 1):
                        raise RuntimeError("Partitioning algorithm has a bug")
                if vs[2] in partitions[p]:
                    if disp[p] != (include_vertex[vs[2]] == 1):
                        raise RuntimeError("Partitioning algorithm has a bug")
            
            for p in range(len(partitions)):

                part = partitions[p]

                if not disp[p]:
                    continue

                verts = []
                for index in partitions[p]:
                    verts.append(nv[index])

                if invert:
                    verts.reverse()

                m.add_face(verts)


