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

if __name__ == '__main__':
    app = wx.App(False)

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

    #meshes = {"cylinder":c1, "cube2": m2, "intersect": m3, "inter":}
    #meshes = {"cube1": m1, "cube2": m2, "intersect": i1}

    frame = MainWindow(meshes = meshes,
                       rois = {},
                       title = "Intersection test")
    app.MainLoop()
    del frame
    del app

