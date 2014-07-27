
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


from __future__ import division
from settings import *

import wx

import re


class MeshPanel(wx.Panel):
    """A wx panel to set options for the loaded meshes.
    """
    def __init__(self, parent, controller, meshnames, *args, **kw):
        self.parent = parent
        self.controller = controller
        self.meshnames = meshnames
        self.cbs = {}
        self.visible = {}
        self.vertices = {}
        super(MeshPanel, self).__init__(parent, *args, **kw)
        self._initUI()
        
    def _initUI(self):   
        self.box = wx.GridBagSizer(3, 10)

        titles = ["Name", "Show?", "Vertices?", "Colour"]
        for i in range(4):
            self.box.Add(wx.StaticText(self, -1, titles[i]), wx.GBPosition(0, i))

        self.box.Add(wx.StaticLine(self, -1), wx.GBPosition(1, 0), span=wx.GBSpan(1, 4), flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=3)

        self.cols = 2

        for meshname in self.meshnames:
            self.addMesh(meshname)

        self.SetAutoLayout(True)
        self.SetSizer(self.box)
        self.Layout()
        self.Bind(wx.EVT_COMBOBOX, self.OnChange)
        self.Bind(wx.EVT_CHECKBOX, self.OnChange)

    def addMesh(self, meshname):
        styles = ["Grey", "Red", "Blue"]

        self.cbs[meshname] = wx.ComboBox(self, -1, choices=styles, style=wx.CB_READONLY, name=meshname+"_style")
        width, height = self.cbs[meshname].GetSize()
        dc = wx.ClientDC (self.cbs[meshname])
        tsize = max ( (dc.GetTextExtent (c)[0] for c in styles) )
        self.cbs[meshname].SetMinSize((tsize+50, height))
        self.cbs[meshname].SetStringSelection(styles[0])
        self.visible[meshname] = wx.CheckBox(self, -1, "", name=meshname+"_visible")
        self.visible[meshname].SetValue(True)
        self.vertices[meshname] = wx.CheckBox(self, -1, "", name=meshname+"_vertices")
        self.vertices[meshname].SetValue(False)
        self.box.Add(wx.StaticText(self, -1, meshname), wx.GBPosition(self.cols, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        self.box.Add(self.visible[meshname], wx.GBPosition(self.cols, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        self.box.Add(self.vertices[meshname], wx.GBPosition(self.cols, 2), flag=wx.ALIGN_CENTER_VERTICAL)
        self.box.Add(self.cbs[meshname], wx.GBPosition(self.cols, 3), flag=wx.ALIGN_CENTER_VERTICAL)
        self.cols += 1

        # enact defaults
        self.controller.setVisible(meshname, True)
        self.controller.setVerticesVisible(meshname, False)
        self.controller.setStyle(meshname, styles[0])

    def OnChange(self, event):
        obj = event.GetEventObject()
        name = obj.GetName()
        if re.match(".*_visible$", name):
            name = re.sub("_visible$", "", name)
            self.controller.setVisible(name, obj.GetValue())
        elif re.match(".*_vertices$", name):
            name = re.sub("_vertices$", "", name)
            self.controller.setVerticesVisible(name, obj.GetValue())
        elif re.match(".*_style$", name):
            name = re.sub("_style$", "", name)
            self.controller.setStyle(name, obj.GetValue())
        else:
            return
        self.controller.Refresh()

