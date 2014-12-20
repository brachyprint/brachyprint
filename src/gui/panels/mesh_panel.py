
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

import wx

from wx.lib.agw.hypertreelist import HyperTreeList
from wx.lib.agw.customtreectrl import TreeItemAttr

import re


class MainWindow(wx.Frame):
    def __init__(self, parent = None, id = -1, title = "Test"):
        # Init
        wx.Frame.__init__(
                self, parent, id, title, size = (400,300),
                style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE
        )

        self.meshPanel = MeshPanel(self, None, [])

        self.meshPanel.addMesh("Skin")
        self.meshPanel.addMesh("Bone")

        self.meshPanel.addRoi("Skin", "ROI1")
        self.meshPanel.addRoi("Skin", "ROI2")

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.meshPanel, 1, wx.EXPAND | wx.ALL, border=5)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()

        # Show
        self.Show(True)


class MeshPanel(HyperTreeList):
    """A wx panel to set options for the loaded meshes.
    """

    def __init__(self, parent, controller, meshnames, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.SUNKEN_BORDER,
                 agwstyle=wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_HIDE_ROOT | wx.TR_NO_LINES):

        super(MeshPanel, self).__init__(parent, id, pos, size, 0, agwstyle)

        self.controller = controller

        # create some columns
        self.AddColumn("Name")
        self.AddColumn("Show?")
        self.SetColumnAlignment(1, wx.ALIGN_LEFT)
        self.AddColumn("Vertices")
        self.AddColumn("Colour")
        self.SetMainColumn(0) # the one with the tree in it...

        # set up column widths
        self.SetColumnWidth(0, 60)
        self.SetColumnWidth(1, 53)
        self.SetColumnWidth(2, 68)
        self.SetColumnWidth(3, 84)

        # clear mesh data
        self.clear()

        # add the initial meshes
        for meshname in self.meshnames:
            self.addMesh(meshname)

        self.SetMinSize(wx.Size(270, 150))

        # bind events
        self.Bind(wx.EVT_COMBOBOX, self.OnChange)
        self.Bind(wx.EVT_CHECKBOX, self.OnChange)


    def addMesh(self, meshname):
        styles = ["Grey", "Red", "Blue"]

        item = self.AppendItem(self.root, meshname)
        self.meshes[meshname] = item

        # create a style combobox
        self.cbs[meshname] = wx.ComboBox(self, -1, choices=styles, style=wx.CB_READONLY, name=meshname+"_style")
        width, height = self.cbs[meshname].GetSize()
        dc = wx.ClientDC (self.cbs[meshname])
        tsize = max ( (dc.GetTextExtent (c)[0] for c in styles) )
        self.cbs[meshname].SetSize((tsize+50, height))
        self.cbs[meshname].SetStringSelection(styles[0])

        self.visible[meshname] = wx.CheckBox(self, -1, "", name=meshname+"_visible")
        self.visible[meshname].SetValue(True)

        self.vertices[meshname] = wx.CheckBox(self, -1, "", name=meshname+"_vertices")
        self.vertices[meshname].SetValue(False)

        self.SetItemImage(item, None, which=wx.TreeItemIcon_Normal)
        self.SetItemImage(item, None, which=wx.TreeItemIcon_Expanded)

        self.SetItemWindow(item, self.visible[meshname], 1)
        self.SetItemWindow(item, self.vertices[meshname], 2)
        self.SetItemWindow(item, self.cbs[meshname], 3)

        # enact defaults
        if self.controller:
            self.controller.setVisible(meshname, True)
            self.controller.setVerticesVisible(meshname, False)
            self.controller.setStyle(meshname, styles[0])


    def addRoi(self, meshname, roiname):
        self.AppendItem(self.meshes[meshname], roiname)


    def hideMesh(self, meshname):
        self.visible[meshname].SetValue(False)
        self.controller.setVisible(meshname, self.visible[meshname].GetValue())
        self.Refresh()
        self.controller.Refresh()


    def clear(self):
        self.cbs = {}
        self.visible = {}
        self.vertices = {}
        self.meshnames = {}

        self.meshes = {}

        self.DeleteAllItems()
        self.root = self.AddRoot("Meshes")

        self.SetPyData(self.root, None)


    def OnChange(self, event):
        obj = event.GetEventObject()
        name = obj.GetName()

        if re.match(".*_visible$", name):
            name = re.sub("_visible$", "", name)
            #self.meshes[name].SetAttributes(TreeItemAttr(colText=(100,100,100)))
            self.controller.setVisible(name, obj.GetValue())
        elif re.match(".*_vertices$", name):
            name = re.sub("_vertices$", "", name)
            self.controller.setVerticesVisible(name, obj.GetValue())
        elif re.match(".*_style$", name):
            name = re.sub("_style$", "", name)
            self.controller.setStyle(name, obj.GetValue())
        else:
            return
        self.Refresh()
        self.controller.Refresh()


if __name__ == '__main__':
    app = wx.App(False)

    frame = MainWindow()

    app.MainLoop()

    del frame
    del app

