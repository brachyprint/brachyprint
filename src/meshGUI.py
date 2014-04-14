#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from __future__ import division
import wx
import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from math import pi, acos, sin, cos, ceil, floor
from itertools import chain
from settings import *
from copy import copy

from gui import MeshCanvas
from gui import MeshController


class ModePanel(wx.Panel):
           
    def __init__(self, parent, rois, *args, **kw):
        super(ModePanel, self).__init__(parent, *args, **kw) 
        self.rois = rois
        self.InitUI()
        
    def InitUI(self):
        box = wx.BoxSizer(wx.VERTICAL)   
        self.rb_rotate = wx.RadioButton(self, label='Rotate',  style=wx.RB_GROUP)
        self.rb_zoom = wx.RadioButton(self, label='Zoom')
        self.rb_edits = {}
        self.rb_selects = {}
        box.Add(self.rb_rotate, 0.5, wx.EXPAND)
        box.Add(self.rb_zoom, 0.5, wx.EXPAND)
        for roiname, roi in self.rois.items():
            self.rb_edits[roiname] = wx.RadioButton(self, label='Edit %s' % roiname)
            box.Add(self.rb_edits[roiname], 0.5, wx.EXPAND)
            if roi.has_key("onSelect"):
                self.rb_selects[roiname] = wx.RadioButton(self, label='Select %s' % roiname)
                box.Add(self.rb_selects[roiname], 0.5, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()

    def GetMode(self):
        if self.rb_rotate.GetValue():  return "Rotate"
        if self.rb_zoom.GetValue(): return "Zoom"  
        for roiname, rb in self.rb_edits.items(): 
            if rb.GetValue(): return "Edit", roiname  
        for roiname, rb in self.rb_selects.items(): 
            if rb.GetValue(): return "Select", roiname

class MeshPanel(wx.Panel):
    '''
        MeshPanel -- display a panel of information about the loaded meshes
    '''
    def __init__(self, parent, meshnames, *args, **kw):
        self.parent = parent
        self.meshnames = meshnames
        self.cbs = {}
        self.visible = {}
        self.vertices = {}
        super(MeshPanel, self).__init__(parent, *args, **kw) 
        self.InitUI()
        
    def InitUI(self):   
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

        self.cbs[meshname] = wx.ComboBox(self, -1, choices=styles, style=wx.CB_READONLY)
        width, height = self.cbs[meshname].GetSize()
        dc = wx.ClientDC (self.cbs[meshname])
        tsize = max ( (dc.GetTextExtent (c)[0] for c in styles) )
        self.cbs[meshname].SetMinSize((tsize+50, height))
        self.cbs[meshname].SetStringSelection(styles[0])
        self.visible[meshname] = wx.CheckBox(self, -1, "")
        self.visible[meshname].SetValue(True)
        self.vertices[meshname] = wx.CheckBox(self, -1, "")
        self.vertices[meshname].SetValue(False)
        self.box.Add(wx.StaticText(self, -1, meshname), wx.GBPosition(self.cols, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        self.box.Add(self.visible[meshname], wx.GBPosition(self.cols, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        self.box.Add(self.vertices[meshname], wx.GBPosition(self.cols, 2), flag=wx.ALIGN_CENTER_VERTICAL)
        self.box.Add(self.cbs[meshname], wx.GBPosition(self.cols, 3), flag=wx.ALIGN_CENTER_VERTICAL)
        self.cols += 1

    def getStyle(self, meshname):
        return self.cbs[meshname].GetValue()

    def getVisible(self, meshname):
        return self.visible[meshname].GetValue()

    def getShowVertices(self, meshname):
        return self.vertices[meshname].GetValue()

    def OnChange(self, event):
        #self.parent.Refresh()
        self.parent.meshPanelChange()


class MainWindow(wx.Frame):
    def __init__(self, parent = None, id = -1, title = "Brachyprint mould viewer", rois = [], meshes={}):
        # Init
        wx.Frame.__init__(
                self, parent, id, title, size = (400,300),
                style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE
        )

        # TextCtrl
        # self.control = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE)

        #self.control = ConeCanvas(self)
        self.modePanel = ModePanel(self, rois)
        self.meshPanel = MeshPanel(self, meshes.keys(), style=wx.SUNKEN_BORDER)

        vbox = wx.BoxSizer(wx.VERTICAL)
        box = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(self.meshPanel, 0.5, wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.modePanel, 0.5, wx.EXPAND)

        self.showgrid = wx.CheckBox(self, label="Show grid")
        vbox.Add(self.showgrid, 0, wx.TOP, 20)

        self.screenshot = wx.Button(self, label="Screenshot")
        vbox.Add(self.screenshot, 0, wx.TOP, 20)

        box.Add(vbox, 0.5, wx.EXPAND)

        # create the meshes
        self.meshes = meshes
        self.meshCanvas = MeshCanvas(self)
        self.meshController = MeshController(self.meshCanvas, self.meshes, rois, self.modePanel, self.meshPanel)
        self.meshCanvas.setController(self.meshController)
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

