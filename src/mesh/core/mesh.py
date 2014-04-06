
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
from ..routes import *

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
        self.maxX, self.minX = None, None
        self.maxY, self.minY = None, None
        self.maxZ, self.minZ = None, None
        self.next_vertex_name = 0
        self.next_face_name = 0
        self.next_volume_name = 0
        self.face_to_vol = {}



    def get_edge(self, v1, v2):
        if self.edges.has_key((v1,v2)):
            return self.edges[(v1,v2)]
        elif self.edges.has_key((v2,v1)):
            return self.edges[(v2,v1)]
        else:
            raise KeyError



    def add_vertex(self, x, y=None, z=None):
        """Function to add a vertex to the mesh.
        
        :param x: x coordinate of the vertex, or optionally a list of coordinates.
        :keyword y: y coordinate of the vertex.
        :keyword z: z coordinate of the vertex.

        """
        if isinstance(x, Vector):
            y = x.y
            z = x.z
            x = x.x
        v = Vertex(x,y,z, self.next_vertex_name)
        self.next_vertex_name += 1
        self.vertices.append(v)
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
        return v

    def add_face(self, v1, v2=None, v3=None):
        """Function to add a face to the mesh.

        :param v1: Vertex 1 of the face or optionally a list of faces.
        :keyword v2: Vertex 2 of the face.
        :keyword v3: Vertex 3 of the face.

        Quadrilateral faces are split simply into two triangles, and higher
        order faces are added by constrained triangulation of the vertices.

        """
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

                plot_it = True
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
        """Function to add a triangular face to the mesh.

        :param v1: vertex 1 of the face
        :param v2: vertex 2 of the face
        :param v3: vertex 3 of the face

        """
        f = Face(self.next_face_name, v1, v2, v3)
        self.next_face_name += 1
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
        for v in [v1, v2, v3]:
            v.add_face(f)

        return f


    def get_path(self, s1, s2):
        s2Postion = s2[0], s2[1], s2[2]
        s2Face = self.faces[s2[3]]
        priority_queue = []
        visited = {}
        if s1[3] == s2[3]:
            return [point_to_point(s1, s2)]
        for v in self.faces[s1[3]].vertices:
            pv = point_to_vertex(s1[0], s1[1], s1[2], v, s2Postion, s2Face)
            heappush(priority_queue, (pv.dist() + pv.crowdist(), pv.dist(), [pv]))	
        while (len(priority_queue) > 0):
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
                        heappush(priority_queue, (dist + new_dist + pv.crowdist(), dist + new_dist, paths + [newPath]))


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

        volumes = [f.signed_volume() for f in self.faces]
        return sum(volumes)


    def surface_area(self):
        """Calculate the surface area of the mesh.

        :returns: Surface area of the mesh.

        """
        areas = [f.area() for f in self.faces]
        return sum(areas)
        

    def closed(self):
        """Checks whether the surface is closed or not, i.e. whether all edges have strictly
        two connected faces.

        :returns: True if the surface is closed.
        """
        for e in self.edges.itervalues():
            if e.lface is None or e.rface is None:
                return False
        return True


    def get_vertex(self, x, y=None, z=None):
        """Function to get a vertex from the mesh, if extant.
        
        :param x: x coordinate of the vertex, or optionally a list of coordinates.
        :keyword y: y coordinate of the vertex.
        :keyword z: z coordinate of the vertex.

        XXX: this is currently very slow!
        """
        if not isinstance(x, Vector):
            x = Vector(x, y, z)

        for v in self.vertices:
            if v == x:
                return v

        return None


#    def allocate_volumes(self):
#        '''Allocate each face to a particular volume.
#
#        '''
#        to_grow = []
#        for face in self.faces:
#            if face.volume is None:
#                face.volume = self.next_volume_name
#                self.face_to_vol[face.name] = face.volume
#                self.next_volume_name += 1
#                self.volumes[face.volume]= [face]
#                to_grow.append(face)
#                while to_grow:
#                    f = to_grow.pop()
#                    for e in f.edges:
#                        for new_face in e.faces():
#                            if new_face.volume is None:
#                                new_face.volume = face.volume
#                                self.face_to_vol[new_face.name] = face.volume
#                                self.volumes[face.volume].append(new_face)
#                                to_grow.append(new_face)
#        

