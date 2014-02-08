#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
import wx
from meshGUI import MainWindow
from settings import *
from mesh import makeMesh
import parseply

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
        f = open(filename)
        meshes[name] = makeMesh(parseply.parseply(f))
        f.close()

    frame = MainWindow(meshes=meshes, 
                       rois = {"Catheters": {"meshname": "Rough Outer", "closed": False}, 
                               "Bridges": {"meshname": "Rough Outer", "closed": False}, 
                               "Extent": {"meshname": "Rough Outer", "closed": True}}, 
                       title = "Fine Cut")
    app.MainLoop()
    del frame
    del app

