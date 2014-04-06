#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
import wx
from meshGUI import MainWindow, roiGUI
from settings import *
import mesh
from octrees import Octree

class OnSelect:
  def __init__(self, outer_mesh, inner_mesh, base_file):
    self.outer_mesh = outer_mesh
    self.inner_mesh = inner_mesh
    self.base_file = base_file
  def __call__(self, outerROI, triangle):
    outer_avoid_edges = outerROI.get_avoidance_edges()
    #Save the cut out mesh to a file
    outerMesh = self.outer_mesh.cloneSubVol(triangle, outer_avoid_edges)

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
    for roi in outerROI.rois:
        for start_outer, end_outer in zip(roi.points, roi.points[1:] + [roi.points[0]]):
            start_distance, start_coords, start_inner = points.by_distance_from_point(start_outer[:3]).next()
            end_distance, end_coords, end_inner = points.by_distance_from_point(end_outer[:3]).next()
            inner_avoid_edges = inner_avoid_edges + [x.edge for x in self.inner_mesh.get_vertex_path(start_inner, end_inner)]
    
    triangle_distance, triangle_coords, triangle_vertex_inner = points.by_distance_from_point(triangle.vertices[0]).next()
    start_triangle = triangle_vertex_inner.faces[0]
    print inner_avoid_edges, start_triangle, start_triangle in self.inner_mesh.faces
    
    innerMesh = self.inner_mesh.cloneSubVol(start_triangle, inner_avoid_edges) 

    newMesh = mesh.Mesh()
    newMesh.add_mesh(outerMesh)
    newMesh.add_mesh(innerMesh, invert = True)
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
        meshes[name] = mesh.fileio.read_ply(filename)

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

