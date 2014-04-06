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
    mesh.primitives.add_cube(m1, 100)
    #self.meshCanvas.addMesh(m1, "cube1")
    #self.meshPanel.addMesh("cube1")

    #mesh.primitives.add_cube(m2, 100, (-48, 48, 48))
 
    m2 = mesh.Mesh()
    mesh.primitives.add_cube(m2, 100, (-38, 48, 48))

    c1 = mesh.Mesh()
    #mesh.primitives.add_cylinder(c1, 50, 40, 50, offset=[1,1,-15])
    mesh.primitives.add_cylinder(c1, 50, 40, 50, offset=[1,1,-10])
    #self.meshCanvas.addMesh(m2, "cube2")
    #self.meshPanel.addMesh("cube2")

    m3 = mesh.manipulate.intersect(m1, c1)
    m4 = mesh.manipulate.intersect(m3, m2)
    m5 = mesh.manipulate.intersect(m1, m2)

    meshes = {"cylinder":c1, "cube2": m2, "cube4": m4, "intersect": m3, "blah": m5}

    frame = MainWindow(meshes = meshes,
                       rois = {},
                       title = "Intersection test")
    app.MainLoop()
    del frame
    del app
