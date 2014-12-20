#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

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

import wx
from meshGUI import MainWindow
from settings import *
import mesh
from octrees import Octree

def list_vertices(mesh, first_vertex, edges):
    current_vertex = first_vertex
    r = [current_vertex]
    for edge in edges:
        if edge.v1 == current_vertex:
           current_vertex = edge.v2
        elif edge.v2 == current_vertex:
           current_vertex = edge.v1
        else:
           raise Exception("edges not connected")
        looked_up_vertex = find_vertex(mesh, current_vertex)
        if looked_up_vertex is not None:
            r.append(looked_up_vertex)
    return r
            

def find_vertex(mesh, vertex):
    for v in mesh.vertices:
        if v == vertex:
            return v
    else:
        print "Missed"

class OnSelect(object):
  def __init__(self, outer_mesh, inner_mesh, base_file):
    self.outer_mesh = outer_mesh
    self.inner_mesh = inner_mesh
    self.base_file = base_file
  def __call__(self, outerROI, triangle):


    #Create an Octree from inner surface
    minx = min([v.x for v in self.inner_mesh.vertices]) - 0.01
    maxx = max([v.x for v in self.inner_mesh.vertices]) + 0.01
    miny = min([v.y for v in self.inner_mesh.vertices]) - 0.01
    maxy = max([v.y for v in self.inner_mesh.vertices]) + 0.01
    minz = min([v.z for v in self.inner_mesh.vertices]) - 0.01
    maxz = max([v.z for v in self.inner_mesh.vertices]) + 0.01
    points = Octree(((minx, maxx), (miny, maxy), (minz, maxz)))
    for v in self.inner_mesh.vertices:
        points.insert((v.x, v.y, v.z), v)

    #Copy extend to inner surface
    inner_avoid_edges = []
    outer_avoid_edges = []
    join_strip = []
    for roi in outerROI.rois:
        for start_outer, end_outer in zip(roi.points, roi.points[1:] + [roi.points[0]]):
            start_outer_vertex = outerROI.mesh.faces[start_outer[3]].nearest_vertex(*start_outer[:3])
            end_outer_vertex = outerROI.mesh.faces[end_outer[3]].nearest_vertex(*end_outer[:3])
            start_distance, start_coords, start_inner = points.by_distance_from_point((start_outer_vertex.x, 
                                                                                       start_outer_vertex.y, 
                                                                                       start_outer_vertex.z)).next()
            end_distance, end_coords, end_inner = points.by_distance_from_point((end_outer_vertex.x,
                                                                                 end_outer_vertex.y, 
                                                                                 end_outer_vertex.z)).next()
            inner_strip = [x.edge for x in self.inner_mesh.get_vertex_path(start_inner, end_inner)]
            outer_strip = [x.edge for x in self.outer_mesh.get_vertex_path(start_outer_vertex,end_outer_vertex)]
            inner_avoid_edges = inner_avoid_edges + inner_strip
            outer_avoid_edges = outer_avoid_edges + outer_strip
            join_strip = join_strip + [(start_inner, inner_strip, start_outer_vertex, outer_strip)]          
    
    triangle_distance, triangle_coords, triangle_vertex_inner = points.by_distance_from_point(triangle.vertices[0]).next()
    start_triangle = triangle_vertex_inner.faces[0]
    innerMesh = self.inner_mesh.cloneSubVol(start_triangle, inner_avoid_edges) 
    print outer_avoid_edges
    outerMesh = self.outer_mesh.cloneSubVol(triangle, outer_avoid_edges)


    newMesh = mesh.Mesh()
    newMesh.add_mesh(outerMesh)
    newMesh.add_mesh(innerMesh, invert = True)
    for current_inner, inner_strip, current_outer, outer_strip in join_strip:
       inner_list = list_vertices(newMesh, current_inner, inner_strip)
       outer_list = list_vertices(newMesh, current_outer, outer_strip)
       while len(inner_list) > 1 or len(outer_list) > 1:
           if len(outer_list) == 1 or (len(inner_list) > 1 and (inner_list[0] - outer_list[1]).magnitude() > (inner_list[1] - outer_list[0]).magnitude()):
               newMesh.add_face(inner_list[0], inner_list[1], outer_list[0])
               inner_list = inner_list[1:]
           else:
               newMesh.add_face(inner_list[0], outer_list[1], outer_list[0])
               outer_list = outer_list[1:]
    for edge in newMesh.edges.values():
        if edge.lface is None or edge.rface is None:
            print edge
    print newMesh.closed()
    stlwriter = mesh.fileio.StlWriter(mesh.fileio.STL_FORMAT_BINARY)
    stlwriter.write(newMesh, "Mould", self.base_file + "mould.stl")

if __name__ == '__main__':
    app = wx.App(False)
    #app = wx.PySimpleApp()        
    openFileDialog = wx.FileDialog(None, "Load", DEFAULT_OUTPUT_DIR, DEFAULT_OUTPUT_FILE, wildcard="*.skin.ply")
    openFileDialog.ShowModal()
    skin_file = openFileDialog.GetPath()
    openFileDialog.Destroy()
    base_filename = skin_file[:-8]

    ply_files = {"Skin": skin_file, "Bone": base_filename + "bone.ply", "Rough Inner": base_filename + "rough.ply", "Rough Outer": base_filename + "external.ply"}

    meshes = {}
    for name, filename in ply_files.items():
        meshes[name] = mesh.Mesh()
        mesh.fileio.read_ply(meshes[name], filename)

    frame = MainWindow(meshes=meshes, 
                       rois = {"Catheters": {"meshname": "Rough Outer", 
                                             "closed": False,
                                             "colour": "red", 
                                             "thickness": 1}, 
                               "Bridges": {"meshname": "Rough Outer", 
                                           "closed": False,
                                           "colour": "blue", 
                                           "thickness": 0.5 }, 
                               "Extent": {"meshname": "Rough Outer", 
                                          "closed": True,
                                          "colour": "green", 
                                          "thickness": 1,
                                          "onSelect": OnSelect(meshes["Rough Outer"], meshes["Rough Inner"], base_filename)}}, 
                       title = "Fine Cut")

    app.MainLoop()
    del frame
    del app

