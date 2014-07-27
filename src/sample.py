#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

import wx
from meshGUI import MainWindow
from settings import *
import mesh

if __name__ == '__main__':
    app = wx.App(False)

    m1 = mesh.Mesh()
    mesh.primitives.add_cuboid(m1, 60, 60, 10)
 
    m2 = mesh.Mesh()
    mesh.primitives.add_cylinder(m2, 2.6, 80, 50, axis=[0,1,0], offset=[5, -10, 0])
    mesh.primitives.add_cylinder(m2, 2.8, 80, 50, axis=[0,1,0], offset=[15, -10, 0])
    mesh.primitives.add_cylinder(m2, 3, 80, 50, axis=[0,1,0], offset=[30, -10, 0])
    mesh.primitives.add_cylinder(m2, 3.2, 80, 50, axis=[0,1,0], offset=[45, -10, 0])
    mesh.primitives.add_cylinder(m2, 3.4, 80, 50, axis=[0,1,0], offset=[55, -10, 0])

    m3 = mesh.manipulate.intersect(m1, m2)

    meshes = {"base": m1, "catheter": m2, "sample": m3}

    frame = MainWindow(meshes = meshes,
                       rois = {},
                       title = "Sample")
    app.MainLoop()
    del frame
    del app

