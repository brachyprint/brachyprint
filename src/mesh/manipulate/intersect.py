
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


from __future__ import division

import mesh

from random import uniform

from mesh.plot import plot_verts


def intersect(m1, m2):
    '''Compute the intersection of m1 and m2.

    :returns: A new mesh with m2 cut out of m1.
    '''

    # check the algorithm assumptions are satisfied
    if not m1.closed():
        raise ValueError("Mesh 'm1' is not a closed surface")

    if not m2.closed():
        raise ValueError("Mesh 'm2' is not a closed surface")

    # algorithm:

        # classify vertices in m1 into inside and outside m2
        # classify vertices in m2 into inside and outside m1

        # for each face in m1
            # for each face in m2
                # if there is an intersection, record the intersection line

        # output all vertices
            # where intersections exists, add extra vertices

        # for each face in m1 and m2
            # if intersections are recorded
                # partition the face along the intersection lines
                # if a partition contains an original vertex included in the output,
                # output the partition
                # recursively classify paritions to output based on crossing of
                # intersections
            # for each partition to output
               # output the face, triangulating if necessary

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

    # create Polygons to represent faces
    m1_polygons = {}
    for f1 in m1.faces:
        m1_polygons[f1.name] = {}
        (vs, u, v, undo) = f1.project2d()
        #vs.reverse()
        p = mesh.Polygon((vs, [(0,2),(2,1),(1,0)]))
        m1_polygons[f1.name]["p"] = p
        m1_polygons[f1.name]["u"] = u
        m1_polygons[f1.name]["v"] = v
        m1_polygons[f1.name]["undo"] = undo

        # add vertices and record mapping
        m1_polygons[f1.name]["map"] = []
        for i in range(3):
            m1_polygons[f1.name]["map"].append(add_vertex(f1.vertices[i], m1_vertices[f1.vertices[i].name]))

    m2_polygons = {}
    for f2 in m2.faces:
        m2_polygons[f2.name] = {}
        (vs, u, v, undo) = f2.project2d()
        p = mesh.Polygon((vs, [(0,2),(2,1),(1,0)]))
        m2_polygons[f2.name]["p"] = p
        m2_polygons[f2.name]["u"] = u
        m2_polygons[f2.name]["v"] = v
        m2_polygons[f2.name]["undo"] = undo

        # add vertices and record mapping
        m2_polygons[f2.name]["map"] = []
        for i in range(3):
            m2_polygons[f2.name]["map"].append(add_vertex(f2.vertices[i], m2_vertices[f2.vertices[i].name]))
        

    # determine all face/face intersections
    # XXX: optimise this using octrees
    for f1 in m1.faces:

        for f2 in m2.faces:

            s = mesh.triangle_triangle_intersect(list(f2.vertices), list(f1.vertices))

            if isinstance(s, list):
                # these two faces intersect
                # add the vertices to the list

                # marry vertices with existing vertices
                for i_s in range(len(s)):
                    s[i_s] = add_vertex(s[i_s], 2)

                u1 = m1_polygons[f1.name]["u"]
                v1 = m1_polygons[f1.name]["v"]
                u2 = m2_polygons[f2.name]["u"]
                v2 = m2_polygons[f2.name]["v"]

                # record m1 and m2 vertices
                verts1 = [0]*len(s)
                verts2 = [0]*len(s)
                for i_s in range(len(s)):
                    verts1[i_s] = m1_polygons[f1.name]["p"].add_vertex(new_vertices[s[i_s]].project2dvector(u1, v1))
                    if verts1[i_s].name == len(m1_polygons[f1.name]["map"]):
                        m1_polygons[f1.name]["map"].append(s[i_s])
                    elif verts1[i_s].name > len(m1_polygons[f1.name]["map"]):
                        raise ValueError

                    verts2[i_s] = m2_polygons[f2.name]["p"].add_vertex(new_vertices[s[i_s]].project2dvector(u2, v2))
                    if verts2[i_s].name == len(m2_polygons[f2.name]["map"]):
                        m2_polygons[f2.name]["map"].append(s[i_s])
                    elif verts2[i_s].name > len(m2_polygons[f2.name]["map"]):
                        raise ValueError

                # record m1 and m2 lines
                for i_s in range(len(s)-1):
                    m1_polygons[f1.name]["p"].add_line(verts1[i_s-1], verts1[i_s])
                    m2_polygons[f2.name]["p"].add_line(verts2[i_s-1], verts2[i_s])

    # create new output mesh
    m = mesh.Mesh()

    # add all the vertices
    nv = []
    for k,v in new_vertices.items():
        if include_vertex[k]:
            nv.append(m.add_vertex(v))
        else:
            nv.append(v)

    # output faces for the outer mesh
    output_faces(m1_polygons, include_vertex, new_vertices, m, nv)
    # output faces for the inner mesh
    output_faces(m2_polygons, include_vertex, new_vertices, m, nv, True)

    return m


def output_faces(polygons, include_vertex, new_vertices, m, nv, invert=False):

    # output the faces from m1
    for k,p in polygons.items():

        # triangulate the face with the new vertices

        # extract the vertex names
        vs = map(lambda x: x.name, p["p"].vertices)
        vs = [p["map"][v] for v in vs]

        if len(vs) < 3:
            # XXX: change this to an Exception
            print "Error!"
        elif len(vs) == 3:
            # no intersection; just add the face
            if include_vertex[vs[0]] and include_vertex[vs[1]] and include_vertex[vs[2]]:
                if invert:
                    m.add_face(nv[vs[1]], nv[vs[0]], nv[vs[2]])
                else:
                    m.add_face(nv[vs[0]], nv[vs[1]], nv[vs[2]])
        else:

            # XXX: change this to an Exception
            if not p["p"].closed():
                print "Warning: intersection polygon is not closed. This is likely to be caused by a bug in the intersection code."
                print p["p"].vertices
                print p["p"].lines
                plot_verts([p["p"].vertices])
                continue

            # partition the surface
            partitions = p["p"].partition()

            # reconstruct the 3D paths from the 2D planar intersection geometry
            paths = []
            for p in partitions:
                verts = [vs[x.name] for x in p]
                paths.append(verts)

            # classify partitions into those to display or not
            ps_i = range(len(paths))
            disp = [None]*len(paths)

            # find the partition that includes the first vertex, and display its
            # partition according to the 
            for p in ps_i:
                if vs[0] in paths[p]:
                    disp[p] = (include_vertex[vs[0]] == 1)
                    part_prev = p
                    break

            # For each vertex in the current path, find any paths that share
            # a vertex. Their display will be the opposite of the adjacent path.
            # Proceed recursively to classify the whole partition.
            def find_all_adj(p_prev):
                for p in ps_i:
                    if disp[p] != None:
                        continue
                    # must share an edge (i.e. two points)
                    if len([i for i in paths[p] if i in paths[p_prev]]) > 1:
                        disp[p] = not disp[p_prev]
                        find_all_adj(p)

            find_all_adj(part_prev)

            for i, path in enumerate(paths):
                if disp[i]:

                    verts = [nv[x] for x in path]

                    # XXX: this shouldn't really require inversion here
                    if not invert:
                        verts.reverse()

                    m.add_face(verts)

            continue

