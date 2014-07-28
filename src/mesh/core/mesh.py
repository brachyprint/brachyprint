
#    Brachyprint -- 3D printing brachytherapy moulds
#    Copyright (C) 2013-14  James Cranch, Martin Green and Oliver Madge
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
A mesh class for the ``mesh'' package.
'''

from __future__ import division
from heapq import heappush, heappop
import triangle
import matplotlib.pyplot as plt
import triangle.plot as plot
from numpy import array
from vector import Vector, nullVector
from vertex import Vertex
from face import Face
from edge import Edge
from routes import *
from routes2 import *
from octrees import *
from scipy.optimize import leastsq



class Mesh(object):
    '''
    Class representing a mesh.
    '''

    def __init__(self):
        self.clear()


    def clear(self):
        self.vertices = []
        self.faces = []
        self.edges = {}
        self.boundary = set()
        self.maxX, self.minX = None, None
        self.maxY, self.minY = None, None
        self.maxZ, self.minZ = None, None
        self.has_fresh_octrees = False
        self.sumX = 0
        self.sumY = 0
        self.sumZ = 0


    def copy(self):
        m = Mesh()
        m.add_mesh(self)
        return m
        

    def get_edge(self, v1, v2):
        if self.edges.has_key((v1,v2)):
            return self.edges[(v1,v2)]
        elif self.edges.has_key((v2,v1)):
            return self.edges[(v2,v1)]
        else:
            raise KeyError

    def add_specific_vertex(self, v):
        """Add a vertex to the mesh."""
        self.vertices.append(v)
        self.update_bounds(v.x, v.y, v.z)

    def add_vertex(self, x, y=None, z=None):
        """Add a vertex to the mesh.
        
        :param x: x coordinate of the vertex, or optionally a list of coordinates.
        :keyword y: y coordinate of the vertex.
        :keyword z: z coordinate of the vertex.
        """
        self.has_fresh_octrees = False
        
        if isinstance(x, Vector):
            y = x.y
            z = x.z
            x = x.x
        self.sumX = self.sumX + x
        self.sumY = self.sumY + y
        self.sumZ = self.sumZ + z
        v = Vertex(x,y,z)
        self.update_bounds(x, y, z)
        self.vertices.append(v)

        return v

    def update_bounds(self, x, y, z):
        if self.maxX is None:
            self.maxX = x
            self.minX = x
            self.maxY = y
            self.minY = y
            self.maxZ = z
            self.minZ = z
        if x > self.maxX: self.maxX = x
        elif x < self.minX: self.minX = x
        if y > self.maxY: self.maxY = y
        elif y < self.minY: self.minY = y
        if z > self.maxZ: self.maxZ = z
        elif z < self.minZ: self.minZ = z

    def centre(self):
        l = len(self.vertices)
        if l:
            return self.sumX / l, self.sumY / l, self.sumZ / l

    def add_face(self, v1, v2=None, v3=None):
        """Add a face to the mesh.

        :param v1: Vertex 1 of the face or optionally a list of faces.
        :keyword v2: Vertex 2 of the face.
        :keyword v3: Vertex 3 of the face.

        Quadrilateral faces are split simply into two triangles, and higher
        order faces are added by constrained Delaunay triangulation of the
        vertices.
        """
        self.has_fresh_octrees = False
        if isinstance(v1, list):
            if len(v1) == 3:
                self.add_triangle_face(v1[0], v1[1], v1[2])
            elif len(v1) == 4:
                self.add_triangle_face(v1[0], v1[1], v1[2])
                self.add_triangle_face(v1[2], v1[3], v1[0])
            elif len(v1) < 3:
                raise TypeError("Must supply at least 3 vertices")
            else:
                # find orthogonal basis vectors from the supplied vertices
                u = v1[1] - v1[0]
                v = None
                for i in range(2, len(v1)):
                    if (v1[1] - v1[i]).cross(u) != nullVector:
                        v = v1[1] - v1[i]
                        break

                if type(v) != Vector:
                    raise ValueError("All points in the face are colinear")

                n = v.cross(u)
                v = n.cross(u)

                points = []
                for i in range(len(v1)):
                    points.append(v1[i])

                segments = []
                for i in range(len(v1)-1):
                    segments.append([i, i+1])
                segments.append([len(v1)-1, 0])

                # project every point into 2d
                for i in range(len(points)):
                    points[i] = points[i].project2d(u, v)

                vertices = dict(vertices=array(points), segments=array(segments))

                plot_it = False
                if plot_it:
                    print vertices

                    ax1 = plt.subplot(121, aspect='equal')
                    triangle.plot.plot(ax1, **vertices)

                    #t = triangle.triangulate(box, 'pc')

                    #ax2 = plt.subplot(122, sharex=ax1, sharey=ax1)
                    #plot.plot(ax2, **t)

                    plt.show()

                # triangulate constraining triangulation to the segment edge
                try:
                    t = triangle.triangulate(vertices, 'pq0')
                except:
                    return

                if not "triangles" in t:
                    raise ValueError("Ill-conditioned face vertices -- unable to produce a triangulation")

                if len(t["triangles"]) > len(points):
                    return
                    raise ValueError("Triangulation added additional vertices")

                # add the triangular faces
                for vertices in t["triangles"]:
                    self.add_triangle_face(v1[vertices[0]], v1[vertices[1]], v1[vertices[2]])
        else:
            self.add_triangle_face(v1, v2, v3)


    def add_triangle_face(self, v1, v2, v3):
        """Add a triangular face to the mesh.

        :param v1: vertex 1 of the face
        :param v2: vertex 2 of the face
        :param v3: vertex 3 of the face
        """
        f = Face(len(self.faces), v1, v2, v3)
        self.faces.append(f)
        for vs, ve in [(v1, v2), (v2, v3), (v3, v1)]:
            if self.edges.has_key((vs, ve)):
                isleft = True
                e = self.edges[(vs, ve)]
            elif self.edges.has_key((ve, vs)):
                isleft = False
                e = self.edges[(ve, vs)]
            else:
                isleft = True
                e = Edge(vs, ve)
                self.edges[(vs, ve)] = e
            e.add_face(f,isleft)
            f.add_edge(e)
            self.boundary.symmetric_difference_update([e])
        for v in [v1, v2, v3]:
            v.add_face(f)
        return f

    def remove_face(self, f):
        """Remove a triangular face from the mesh.
        """
        for vertex in f.vertices:
            vertex.remove_face(f)
        for edge in f.edges:
            edge.remove_face(f)
            if edge.lface is None and edge.rface is None:
                self.edges.pop((edge.v1,edge.v2))
        self.faces.remove(f)
        
    def get_planar_path(self,p1,f1,p2,f2,p3):
        """Consider points p1 on face f1, p2 on face f2, and a third point
        p3. We consider paths from p1 to p2 obtained by intersecting
        the mesh with the plane through p1, p2 and p3: we return the
        shorter such path.
        """
        fn = lambda p: (p-p1).cross(p-p2).dot(p-p3)

        if f1==f2:
            return Route([Step(f1,FacePoint(f1,p1),FacePoint(f1,p2))])

        paths = []
        def pursue(e2):
            f = f1
            x1 = fn(e2.v1)
            x2 = fn(e2.v2)
            if min(x1,x2) <= 0 <= max(x1,x2):
                q2 = e2.zero_point(fn)
                l = [Step(f1,FacePoint(f1,p1),EdgePoint(e2,q2))]
                while True:
                    e1 = e2
                    q1 = q2
                    f = e2.face_on_other_side(f)
                    if f is None:
                        return None
                    if f == f2:
                        l.append(Step(f,EdgePoint(e1,q1),FacePoint(f2,p2)))
                        paths.append(Route(l))
                        return None
                    else:
                        for e2 in f.edges:
                            if e2 != e1:
                                x1 = fn(e2.v1)
                                x2 = fn(e2.v2)
                                if min(x1,x2) <= 0 <= max(x1,x2):
                                    q2 = e2.zero_point(fn)
                                    l.append(Step(f,EdgePoint(e1,q1),EdgePoint(e2,q2)))
                                    break

        for e2 in f1.edges:
            pursue(e2)

        return min(paths,key=lambda r: r.dist())

    def get_path(self, s1, s2):
        """A hybrid path-finding algorithm.

        We use the A* algorithm to find the shortest path from s1 to
        s2 along edges. Then we fit a sphere to that, consider the
        plane through s1, s2 and the centre, and intersect that with
        the mesh to produce a path.

        s1 and s2 are 4-tuples in the form (x,y,z,n), where n is the
        index of the face on which they lie.
        """

        paths = self.get_edge_path(s1, s2)
        points = set(point for path in paths for point in path.points())
        def err_func((cx, cy, cz, radius), points):
            return [((px - cx) ** 2 + (py - cy) ** 2 + (pz - cz) ** 2) ** 0.5 - radius for (px, py, pz) in points]
        try:
            (cx, cy, cz, radius), found = leastsq(err_func, (0, 0, 0, 0), args=(points))
            if found not in [1,2,3,4]:
                raise Exception 
        except:
            cx, cy, cz = self.centre()
        t = self.get_planar_path(Vector(s1[:3]), self.faces[s1[3]], Vector(s2[:3]), self.faces[s2[3]], Vector(cx, cy, cz))
        return [t]

    def get_edge_path(self, s1, s2):
        """
        Find a path from s1 to s2 through edges (using the A*
        algorithm).

        s1 and s2 are 4-tuples in the form (x,y,z,n), where n is the
        index of the face on which they lie.
        """
        s2Position = s2[0], s2[1], s2[2]
        s2Face = self.faces[s2[3]]
        priority_queue = []
        visited = {}
        if s1[3] == s2[3]:
            return [point_to_point(s1, s2)]
        for v in self.faces[s1[3]].vertices:
            pv = point_to_vertex(s1[0], s1[1], s1[2], v, s2Position, s2Face)
            heappush(priority_queue, (pv.dist() + pv.crowdist(), pv.dist(), [pv]))	
        while priority_queue:
            dist_plus_crow, dist, paths = heappop(priority_queue)
            lastPath = paths[-1]
            end = lastPath.end()
            if end not in visited:
                if lastPath.finished():
                    #Finished!
                    return paths
                else:
                    visited[end] = True
                    for newPath in lastPath.new_Paths():
                        new_dist = newPath.dist()
                        heappush(priority_queue, (dist + new_dist + newPath.crowdist(), dist + new_dist, paths + [newPath]))


    def get_vertex_path(self, v1, v2):
        priority_queue = []
        visited = {}
        for vertex, edge in v1.adjacent_vertices():
            fe = follow_edge_vertex_path(v1, vertex, edge, v2)
            heappush(priority_queue, (fe.dist() + fe.crowdist(), fe.dist(), [fe]))	
        while priority_queue:
            dist_plus_crow, dist, paths = heappop(priority_queue)
            lastPath = paths[-1]
            end = lastPath.end
            if end not in visited:
                if lastPath.finished():
                    #Finished!
                    return paths
                else:
                    visited[end] = True
                    for newPath in lastPath.new_Paths():
                        new_dist = newPath.dist()
                        heappush(priority_queue, (dist + new_dist + newPath.crowdist(), dist + new_dist, paths + [newPath]))


    def cloneSubVol(self, triangle, avoidEdges):
        vertex_map = {}
        faces_copied = [triangle]
        to_grow = [triangle]
        newMesh = Mesh()
        i = 0
        while to_grow:
            i = i +1
            if i % 100 == 0:
                print i, len(to_grow), len(faces_copied), len(self.faces)
            f = to_grow.pop()
            for v in f.vertices:
                if not vertex_map.has_key(v):
                    vertex_map[v] = newMesh.add_vertex(v.x, v.y, v.z)
            newMesh.add_face(*[vertex_map[v] for v in f.vertices])
            for e in f.edges:
                if e not in avoidEdges:
                    for neighbouring_face in e.faces():
                        if (neighbouring_face is not f) and (neighbouring_face not in faces_copied):
                            faces_copied.append(neighbouring_face)
                            to_grow.append(neighbouring_face)
                else:
                    print "AVOID"
        #newMesh.allocate_volumes()
        return newMesh


    def volume(self):
        """Calculate the volume of the mesh.

        :returns: Volume of the mesh.
        """
        # check that the mesh is a single closed volume
        if not self.closed():
            raise ValueError("Can only compute the volume of meshes containing closed surfaces.")

        return abs(sum(f.signed_volume() for f in self.faces))


    def solid_centroid(self):
        """Calculate the centre of mass of the mesh.

        The mesh is regarded as the boundary of a uniform solid object.

        :returns: Vector() representing centre of mass.
        """
        if not self.closed():
            raise ValueError("Can only compute the centroid of meshes representing closed surfaces")

        vol = 0
        pos = Vector(0,0,0)
        for f in self.faces:
            v = f.signed_volume()
            vol += v
            pos += f.centroid()*v
        return pos*(3/(vol*4))


    def surface_centroid(self):
        """Calculate the centre of mass of the mesh.

        The mesh is regarded as a uniform lamina for the purposes of the
        calculation.

        :returns: Vector() representing centre of mass.
        """

        area = 0
        pos = Vector(0,0,0)
        for f in self.faces:
            a = f.area()
            area += a
            pos += f.centroid()*a
        return pos/area


    def surface_area(self):
        """Calculate the surface area of the mesh.

        :returns: Surface area of the mesh.
        """
        areas = [f.area() for f in self.faces]
        return sum(areas)


    def closed(self):
        """Checks whether the mesh contains only closed surfaces.

        More specifically, check whether all edges have strictly two connected
        faces.

        :returns: True if the surface is closed.
        """
        return not(self.boundary)


    def add_mesh(self, mesh, invert = False):
        """Copy all vertices and faces from another mesh to this one.

        :param mesh: the other mesh to add.
        :keyword invert: invert every face if True, i.e. turn the added mesh inside out.
        """
        vertex_map = dict((v,self.add_vertex(v.x, v.y, v.z)) for v in mesh.vertices)
        for face in mesh.faces:
            vertices = [vertex_map[vertex] for vertex in face.vertices]
            if invert:
                self.add_triangle_face(vertices[0], vertices[2], vertices[1])
            else:
                self.add_triangle_face(vertices[0], vertices[1], vertices[2])
        

    def add_regular_subdivision(self, mesh, n, invert=False):
        """
        Copy all vertices and faces from another mesh into this one, but
        subdivided such that every edge is split into n equal parts.
        """

        vvertices = dict((v,self.add_vertex(v.x,v.y,v.z)) for v in mesh.vertices)

        evertices = {}
        for e in m.edges.itervalues():
            for r in xrange(1,n):
                s = n-r
                v = self.add_vertex((e.v1*r + e.v2*s)/n)
                evertices[(e.v1,e.v2,r,s)] = v
                evertices[(e,v2,e.v1,s,r)] = v

        for f in m.faces:
            u,v,w = f.vertices
            fvertices = {}
            for r in xrange(1,n-1):
                for s in xrange(1,n-r):
                    t = n-r-s
                    fvertices[(r,s,t)] = self.add_vertex((u*r + v*s + w*t)/n)

            for r in xrange(1,n):
                s = n-r
                fvertices[(r,s,0)] = evertices[(u,v,r,s)]
                fvertices[(0,r,s)] = evertices[(v,w,r,s)]
                fvertices[(s,0,r)] = evertices[(w,u,r,s)]

            fvertices[(n,0,0)] = vvertices[u]
            fvertices[(0,n,0)] = vvertices[v]
            fvertices[(0,0,n)] = vvertices[w]

            for r in xrange(0,n):
                for s in xrange(0,n-r):
                    t = n-r-s-1
                    self.add_face(fvertices[(r+1,s,t)],fvertices[(r,s+1,t)],fvertices[(r,s,t+1)])

            for r in xrange(0,detail_level-1):
                for s in xrange(0,detail_level-r-1):
                    t = detail_level-r-s-2
                    mesh.add_face(fvertices[(r,s+1,t+1)],fvertices[(r+1,s,t+1)],fvertices[(r+1,s+1,t)])


    def get_vertex(self, x, y=None, z=None):

        """Get a vertex from the mesh, if extant.
        
        :param x: x coordinate of the vertex, or optionally a list of coordinates.
        :keyword y: y coordinate of the vertex.
        :keyword z: z coordinate of the vertex.
        """

        if isinstance(x, Vector):
            x,y,z = x.x,x.y,x.z

        if self.vertices:
            self.ensure_fresh_octrees()
            return self.vertex_octree.get((x,y,z))
        else:
            return None


    def ensure_fresh_octrees(self):
        if not(self.has_fresh_octrees):
            self.has_fresh_octrees = True
            if self.vertices is None:
                self.vertex_octree = None
                self.face_octree = None
            else:
                epsilon = 0.1
                b = ((self.minX-epsilon,self.maxX+epsilon),
                     (self.minY-epsilon,self.maxY+epsilon),
                     (self.minZ-epsilon,self.maxZ+epsilon))

                self.vertex_octree = Octree(b)
                for v in self.vertices:
                    self.vertex_octree.insert((v.x,v.y,v.z),v)

                self.face_octree = BlobOctree(b)
                for f in self.faces:
                    p = f.centroid()
                    self.face_octree.insert((p.x,p.y,p.z),f.bounding_box(),f)

    def split_edge(self, vertex, edge):
        """Add the vertex along the edge and retriangulate"""
        assert vertex not in [edge.v1, edge.v2]
        new_faces = []
        for face in [edge.lface, edge.rface]:
            if face is not None:
                new_faces = new_faces + self.split_edge_one_face(vertex, edge, face)
        return new_faces
        
    def split_edge_one_face(self, vertex, edge, face): 
        """Remove the face, and make two new triangles split along the edge at vertex"""
        assert vertex not in face.vertices
        self.remove_face(face)
        third_vertex = next(v for v in face.vertices if v not in (edge.v1, edge.v2))
        third_vertex_index = face.vertices.index(third_vertex)
        first_vertex = face.vertices[(third_vertex_index + 1) % 3]
        second_vertex = face.vertices[(third_vertex_index + 2) % 3]
        return [self.add_triangle_face(first_vertex, vertex, third_vertex),
                self.add_triangle_face(third_vertex, vertex, second_vertex)]

    def split_face(self, vertex, face):
        """Add the vertex within the face and retriangulate"""
        self.remove_face(face)
        return [self.add_triangle_face(face.vertices[0], face.vertices[1], vertex),
                self.add_triangle_face(face.vertices[1], face.vertices[2], vertex),
                self.add_triangle_face(face.vertices[2], face.vertices[0], vertex)]


