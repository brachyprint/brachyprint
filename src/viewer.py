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
from points import expand, make_ply



if __name__ == '__main__':
    app = wx.App(False)
    #app = wx.PySimpleApp()        
    #openFileDialog = wx.FileDialog(None, "Load", DEFAULT_OUTPUT_DIR, DEFAULT_OUTPUT_FILE, wildcard="*.ply")
    #openFileDialog.ShowModal()
    #f = openFileDialog.GetPath()
    #openFileDialog.Destroy()


    meshes = {}
    meshes["1"] = mesh.Mesh()
    mesh.fileio.read_ply(meshes["1"], "/home/martin/m1.ply")
    meshes["2"] = mesh.Mesh()
    mesh.fileio.read_ply(meshes["2"], "/home/martin/m2.ply")
    meshes["3"] = mesh.Mesh()
    mesh.fileio.read_ply(meshes["3"], "/home/martin/m3.ply")

    frame = MainWindow(meshes=meshes, 
                       rois = {}, 
                       title = "Viewer",
                       vertex_size = 0.03)
    app.MainLoop()
    del frame
    del app

