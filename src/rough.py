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

class OnSelect(object):
  def __init__(self, mesh, base_file):
    self.mesh = mesh
    self.base_file = base_file
  def __call__(self, roiGUI, triangle):
    avoid_edges = []
    for roi in roiGUI.rois:
        avoid = []
        for paths in roi.paths:
            start = None
            previous_vertex = None
            for path in paths:
                for point in path.points():
                    if start != point:#if first point != last point
                        vertex = point.splitmesh(self.mesh)
                        if previous_vertex is not None:
                            avoid.append(self.mesh.edges[(vertex, previous_vertex)])#Need an edge not a vertex!!
                        previous_vertex = vertex
                        if start is None:
                            start = point
        avoid_edges.append(avoid)                

    #avoid_edges = roiGUI.get_avoidance_edges()
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
        meshes[name] = mesh.Mesh()
        mesh.fileio.read_ply(meshes[name], filename)

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

