#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from __future__ import division
import wx
from settings import *
import re

from gui import MeshCanvas
from gui import MeshController

from gui.tools import RotateTool, ZoomTool, RoiTool

class ModePanel(wx.Panel):
    """A class to select the current tool.
    """
    def __init__(self, parent, controller, tools, *args, **kw):
        super(ModePanel, self).__init__(parent, *args, **kw) 
        self.controller = controller
        self.tools = tools
        self._initUI()

    def getOnChangedHandler(self, tool, subtool):
        def OnChanged(event):
            self.controller.selectTool(tool, subtool)
        return OnChanged

    def _initUI(self):
        box = wx.BoxSizer(wx.VERTICAL)
        self.rb = {}
        style = wx.RB_GROUP
        for i in range(len(self.tools)):
            name = self.tools[i].name
            subtools = self.tools[i].getSubTools()
            for j in range(len(subtools)):
                label = subtools[j]
                self.rb[label] = wx.RadioButton(self, label=label, style=style, name=name)
                style = 0 # only apply the RB_GROUP style to the first RadioButton
                box.Add(self.rb[label], 0.5, wx.EXPAND)
                self.rb[label].Bind(wx.EVT_RADIOBUTTON, self.getOnChangedHandler(name, j))

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()

        self.controller.selectTool(self.tools[0].name)


class MeshPanel(wx.Panel):
    """MeshPanel -- display a panel of information about the loaded meshes
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
        styles = ["Red", "Blue"]

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


class MainWindow(wx.Frame):
    def __init__(self, parent = None, id = -1, title = "Brachyprint mould viewer", rois = [], meshes={}, tools=[RotateTool("Rotate"), ZoomTool("Zoom")]):
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
        self.meshes = meshes
        self.meshCanvas = MeshCanvas(self)
        self.meshController = MeshController(self.meshCanvas, self.meshes)
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

