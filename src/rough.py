#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
import wx
from meshGUI import MainWindow
from settings import *
import mesh
from octrees import Octree
from points import expand, make_ply

class OnSelect:
  def __init__(self, mesh, base_file):
    self.mesh = mesh
    self.base_file = base_file
  def __call__(self, roiGUI, triangle):
    avoid_edges = roiGUI.get_avoidance_edges()
    #Save the cut out mesh to a file
    roughcut = self.mesh.cloneSubVol(triangle, avoid_edges)
    print "Saving"
    mesh.fileio.write_ply(roughcut, self.base_file + "rough.ply")

    #Expand cut out mesh and save that to a file called external
    minx = min([v.x for v in roughcut.vertices]) - 0.01
    maxx = max([v.x for v in roughcut.vertices]) + 0.01
    miny = min([v.y for v in roughcut.vertices]) - 0.01
    maxy = max([v.y for v in roughcut.vertices]) + 0.01
    minz = min([v.z for v in roughcut.vertices]) - 0.01
    maxz = max([v.z for v in roughcut.vertices]) + 0.01
    points = Octree(((minx, maxx), (miny, maxy), (minz, maxz)))
    for v in roughcut.vertices:
        n = v.normal()
        points.insert((v.x, v.y, v.z), (n.x, n.y, n.z))
    external = expand(points, MOULD_THICKNESS)
    make_ply(external, self.base_file + "external", poisson_depth = POISSON_DEPTH)
    make_ply(points, self.base_file + "external_base", poisson_depth = POISSON_DEPTH)

if __name__ == '__main__':
    app = wx.App(False)
    #app = wx.PySimpleApp()        
    openFileDialog = wx.FileDialog(None, "Load", DEFAULT_OUTPUT_DIR, DEFAULT_OUTPUT_FILE, wildcard="*.skin.ply")
    openFileDialog.ShowModal()
    skin_file = openFileDialog.GetPath()
    openFileDialog.Destroy()
    base_filename = skin_file[:-8]

    ply_files = {"Skin": skin_file, "Bone": base_filename + "bone.ply"}

    meshes = {}
    for name, filename in ply_files.items():
        meshes[name] = mesh.fileio.read_ply(filename)

    frame = MainWindow(meshes=meshes, 
                       rois = {"Rough Cut": {"meshname": "Skin", 
                                             "closed": True,
                                             "colour": "red", 
                                             "thickness": 1,
                                             "onSelect": OnSelect(meshes["Skin"], base_filename)}}, 
                       title = "Rough Cut")
    app.MainLoop()
    del frame
    del app

