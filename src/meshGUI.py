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

from __future__ import division
from settings import *

import wx

from gui import MeshCanvas
from gui import MeshController

from gui.tools import RotateTool, ZoomTool, RoiTool, DebugTool
from gui.panels import ModePanel, MeshPanel


class MainWindow(wx.Frame):
    def __init__(self, parent = None, id = -1, title = "Brachyprint mould viewer", rois = [], meshes={}, tools=[RotateTool("Rotate"), ZoomTool("Zoom"), DebugTool("Debug")]):
        # Init
        wx.Frame.__init__(
                self, parent, id, title, size = (400,300),
                style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE
        )

        i=0
        for name, roi in rois.items():
            i+=1
            tools.append(RoiTool(name, roi))

        # create the mesh view widget and controller
        self.meshCanvas = MeshCanvas(self)
        self.meshController = MeshController(self, self.meshCanvas, meshes)
        self.meshCanvas.setController(self.meshController)

        # add the GUI tools to the controller
        for tool in tools:
            self.meshController.addTool(tool)

        # create the panels to select the mesh options and the GUI tool
        self.meshPanel = MeshPanel(self, self.meshController, meshes.keys(), style=wx.SUNKEN_BORDER)
        self.modePanel = ModePanel(self, self.meshController, tools)

        vbox = wx.BoxSizer(wx.VERTICAL)
        box = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(self.meshPanel, 0.5, wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.modePanel, 0.5, wx.EXPAND)

        self.showgrid = wx.CheckBox(self, label="Show grid")
        vbox.Add(self.showgrid, 0, wx.TOP, 20)

        self.screenshot = wx.Button(self, label="Screenshot")
        vbox.Add(self.screenshot, 0, wx.TOP, 20)

        box.Add(vbox, 0.5, wx.EXPAND)

        box.Add(self.meshCanvas, 1, wx.EXPAND)

        self.meshPanel.parent = self.meshController

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()

        self.showgrid.Bind(wx.EVT_CHECKBOX, lambda x: self.meshCanvas.OnDraw())
        #self.screenshot.Bind(wx.EVT_BUTTON, lambda x: self.meshCanvas.Screenshot("screenshot.png", wx.BITMAP_TYPE_PNG))
        self.screenshot.Bind(wx.EVT_BUTTON, lambda x: self.meshCanvas.Screenshot("screenshot.jpg", wx.BITMAP_TYPE_JPEG))

        # StatusBar
        #self.CreateStatusBar()

        # Filemenu
        filemenu = wx.Menu()

        # Filemenu - About
        menuitem = filemenu.Append(-1, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, menuitem) # here comes the event-handler
        # Filemenu - Separator
        filemenu.AppendSeparator()

        # Filemenu - Exit
        menuitem = filemenu.Append(-1, "E&xit", "Terminate the program")
        self.Bind(wx.EVT_MENU, self.OnExit, menuitem) # here comes the event-handler

        # Menubar
        menubar = wx.MenuBar()
        menubar.Append(filemenu,"&File")
        self.SetMenuBar(menubar)

        # Show
        self.Show(True)

        # Maximise the window
        self.Maximize()

    def Refresh(self):
        self.meshCanvas.Refresh(False)

    def OnAbout(self, event):
        message = "Viewer for brachyprint moulds"
        caption = "Brachyprint mould viewer"
        wx.MessageBox(message, caption, wx.OK)

    def OnExit(self, event):
        self.Close(True) # Close the frame.

