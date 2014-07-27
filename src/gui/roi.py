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


from OpenGL.GL import *
from OpenGL.GLUT import *
from math import pi, acos

from copy import copy


class ROI:
    def __init__(self):
        self.paths = []
        self.points = []

    def new_point(self, x, y, z, face_name, end, index):
        if index is not None:
            print self.points
            self.points = self.points[:index + 1] + [(x, y, z, face_name)] + self.points[index+1:]
            temp = copy(self.paths)
            self.paths = temp[:index] + [None, None] + temp[index+1:]
            print self.points
            return index + 1
        elif end:
            self.points.append((x, y, z, face_name))
            if len(self.points) > 1:
                self.paths.append(None)
            return len(self.points) - 1
        else:
            self.points = [(x, y, z, face_name)] + self.points
            if len(self.points) > 1:
                self.paths = [None] + self.paths
            return 0

    def being_drawn(self):
        return len(self.points) == 0 or len(self.paths) < len(self.points)

    def is_empty(self):
        return len(self.points) == 0

    def is_last(self, i):
        return i == len(self.points) - 1

    def remove_point(self, i):
        if i > 0:
            if i < len(self.paths):
                self.paths =  self.paths[:i - 1] + [None] +  self.paths[i + 1:]
            else:
                self.paths =  self.paths[:i - 1]
        else:
            if len(self.paths) == len(self.points):
                self.paths =  self.paths[1:-1] + [None]
            else:
                self.paths =  self.paths[1:]
        self.points = self.points[:i] + self.points[i + 1:]

COLOURS = {"red": (1,0.2,0.2), "green": (0.2, 1,0.2), "blue":(0.2,0.2,1),}

class RoiGUI:
    def __init__(self, mesh, meshname, closed, colour="green", thickness = 1, onSelect=None):
        self.meshname = meshname
        self.mesh = mesh
        self.closed = closed
        self.onSelect = onSelect
        self.rois = []
        self.current_roi = None
        self.current_point_index = None
        self.pointlookup = []
        self.linelookup = []
        self.colour = colour
        self.thickness = thickness

    def InitGL(self):
        self.line_list = glGenLists(1)
        self.sphere_list = glGenLists(1)
        self.compile_sphere_list()
        self.compile_line_list()

    def new_roi(self):
        r = ROI()
        self.rois.append(r)
        return r

    def new_point(self, x, y, z, face_name, end = True, index=None):
        print "Start", index
        if self.current_roi:
            self.current_point_index = self.current_roi.new_point(x, y, z, face_name, end, index)

    def move_point(self, i, x, y, z, face_name):
        if self.current_roi:
            self.current_roi.points[i] = (x, y, z, face_name)
            if i > 0:
                self.current_roi.paths[i - 1] = None
            else:
                if not self.current_roi.being_drawn():
                    self.current_roi.paths[-1] = None
            if i < len(self.current_roi.paths):
                self.current_roi.paths[i] = None
            else:
                if not self.current_roi.being_drawn():
                    self.current_roi.paths[0] = None
            
    def complete(self):
        assert self.current_roi.being_drawn() == True
        if self.closed == True:
            self.current_roi.paths.append(None)

    def compile_sphere_list(self):
        name = 0
        self.pointlookup = []
        glNewList(self.sphere_list, GL_COMPILE)
        glMatrixMode(GL_MODELVIEW)
        for roi in self.rois:
            for i, sphere in enumerate(roi.points):
                glPushMatrix()
                glPushName(name)
                self.pointlookup.append((roi, i))
                name = name + 1
                glTranslatef(sphere[0], sphere[1], sphere[2])
                glColor3f(*COLOURS[self.colour])
                glutSolidSphere(5 * self.thickness, 10, 10)
                glPopName()
                glPopMatrix()
        if self.current_point_index is not None:
            sphere = self.current_roi.points[self.current_point_index]
            glPushMatrix()
            glTranslatef(sphere[0], sphere[1], sphere[2])
            glColor3f(1,1,1)
            glutSolidSphere(6 * self.thickness, 11, 11)
            glPopMatrix()
        glEndList()    

    def compile_line_list(self):
        name = 0
        self.linelookup = []
        glNewList(self.line_list, GL_COMPILE)
        glColor3f(*COLOURS[self.colour])
        for roi in self.rois:
            for index, path_list in enumerate(roi.paths):
                glPushName(name)
                for path in path_list:
                    self.linelookup.append((roi, index))
                    name = name + 1
                    for start, end in path.points():
                        dx = start[0] - end[0]
                        dy = start[1] - end[1]
                        dz = start[2] - end[2]
                        length_d = (dx ** 2 + dy ** 2 + dz ** 2) ** 0.5
                        if length_d > 0:
                            #axis of rotation = (0, 0, 1) cross (dx, dy, dz) = (-dy, dx, 0)
                            #angle to rotate = 180.0 / pi * acos((0,0,1).(dx, dy, dz) / (dx, dy, dz).(dx, dy, dz))
                            glPushMatrix()
                            glTranslatef(start[0], start[1], start[2])
                            glRotatef(180.0 / pi * acos(dz / length_d), -dy, dx, 0)
                            glutSolidSphere(2 * self.thickness, 10, 10)
                            glutSolidCylinder(2 * self.thickness, -length_d, 20 ,20)
                            glPopMatrix()
                glPopName() 
        glEndList()

    def update(self):
        for roi in self.rois:
            for index, path in enumerate(roi.paths):
                if path is None:
                    if index + 1 < len(roi.points):
                        roi.paths[index] = self.mesh.get_path(roi.points[index], roi.points[index + 1])
                    else:
                        roi.paths[index] = self.mesh.get_path(roi.points[index], roi.points[0])
        self.compile_sphere_list()
        self.compile_line_list()

    def sphere_list_length(self):
        return len(self.pointlookup)

    def line_list_length(self):
        return len(self.linelookup)

    def get_avoidance_edges(self):
        avoid_edges = []
        for roi in self.rois:
            paths = sum(roi.paths, [])
            edges = sum([path.get_edges() for path in paths], [])
            #Make list of edges to avoid.  Where there is a point in the middle of a triangle, an extra edge needs to be found.
            #such that a full ring of avoidance edges is created.
            #Find intial vertex
            if edges[-1].v1 in [edges[0].v1, edges[0].v2]:
                vertex = edges[-1].v1
            elif edges[-1].v2 in [edges[0].v1, edges[0].v2]:
                vertex = edges[-1].v2
            else:
                for extra_edge in edges[-1].v1.edges:
                    if extra_edge.v1 == edges[-1].v1 and extra_edge.v2 in [edges[0].v1, edges[0].v2]:
                        avoid_edges.append(extra_edge)
                        vertex = extra_edge.v2
                        break
                    if extra_edge.v2 == edges[-1].v1 and extra_edge.v1 in [edges[0].v1, edges[0].v2]:
                        avoid_edges.append(extra_edge)
                        vertex = extra_edge.v1
                        break
                for extra_edge in edges[-1].v2.edges:
                    if extra_edge.v1 == edges[-1].v2 and extra_edge.v2 in [edges[0].v1, edges[0].v2]:
                        avoid_edges.append(extra_edge)
                        vertex = extra_edge.v2
                        break
                    if extra_edge.v2 == edges[-1].v2 and extra_edge.v1 in [edges[0].v1, edges[0].v2]:
                        avoid_edges.append(extra_edge)
                        vertex = extra_edge.v1
                        break
            print "VERTEX", vertex
            #Go around the loop of edges, adding them to the avoidance list, and adding extra edges where necessary.
            for i, edge in enumerate(edges):
                print i
                if edge.v1 == vertex:
                    vertex = edge.v2
                    avoid_edges.append(edge)
                elif edge.v2 == vertex:
                    vertex = edge.v1
                    avoid_edges.append(edge)
                else:
                    for extra_edge in vertex.edges:
                        if extra_edge.v1 == vertex and extra_edge.v2 == edge.v1:
                            avoid_edges.append(extra_edge)
                            avoid_edges.append(edge)
                            vertex = edge.v2
                            break
                        elif extra_edge.v1 == vertex and extra_edge.v2 == edge.v2:
                            avoid_edges.append(extra_edge)
                            avoid_edges.append(edge)
                            vertex = edge.v1
                            break
                        elif extra_edge.v2 == vertex and extra_edge.v1 == edge.v1:
                            avoid_edges.append(extra_edge)
                            avoid_edges.append(edge)
                            vertex = edge.v2
                            break
                        elif extra_edge.v2 == vertex and extra_edge.v1 == edge.v2:
                            avoid_edges.append(extra_edge)
                            avoid_edges.append(edge)
                            vertex = edge.v1
                            break
                    else:
                        assert False
                        avoid_edges.append(edge)
        return avoid_edges
