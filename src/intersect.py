#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
import wx
from meshGUI import MainWindow
from settings import *
import mesh

if __name__ == '__main__':
    app = wx.App(False)
    #app = wx.PySimpleApp()        
    #openFileDialog = wx.FileDialog(None, "Load", DEFAULT_OUTPUT_DIR, DEFAULT_OUTPUT_FILE, wildcard="*.skin.ply")
    #openFileDialog.ShowModal()
    #skin_file = openFileDialog.GetPath()
    #openFileDialog.Destroy()
    #base_filename = skin_file[:-8]

    # add a cube mesh to the display
    meshes = {}
    m1 = mesh.Mesh()
    mesh.primitives.make_cube(m1, 100)
    #self.meshCanvas.addMesh(m1, "cube1")
    #self.meshPanel.addMesh("cube1")

    m2 = mesh.Mesh()
    mesh.primitives.make_cube(m2, 100, (-48, 48, 48))
    #self.meshCanvas.addMesh(m2, "cube2")
    #self.meshPanel.addMesh("cube2")

    m3 = mesh.manipulate.intersect(m1, m2)

    meshes = {"cube2": m2, "cube3": m3}

    frame = MainWindow({},
                       rois = {},
                       title = "Intersection test",
                       meshes = meshes)
    app.MainLoop()
    del frame
    del app
