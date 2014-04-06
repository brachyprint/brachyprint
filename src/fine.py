#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
import wx
from meshGUI import MainWindow
from settings import *
import mesh

class OnSelect:
  def __init__(self, outer_mesh, inner_mesh, base_file):
    self.outer_mesh = outer_mesh
    self.inner_mesh = inner_mesh
    self.base_file = base_file
  def __call__(self, roiGUI, triangle):
    avoid_edges = roiGUI.get_avoidance_edges()
    #Save the cut out mesh to a file
    roughcut = self.mesh.cloneSubVol(triangle, avoid_edges)

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

