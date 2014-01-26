#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
import wx
from meshGUI import MainWindow
from settings import *

if __name__ == '__main__':
    app = wx.App(False)
    #app = wx.PySimpleApp()        
    openFileDialog = wx.FileDialog(None, "Load", DEFAULT_OUTPUT_DIR, DEFAULT_OUTPUT_FILE, wildcard="*.skin.ply")
    openFileDialog.ShowModal()
    skin_file = openFileDialog.GetPath()
    openFileDialog.Destroy()
    base_filename = skin_file[:-8]
    frame = MainWindow({"Skin": skin_file, "Bone": base_filename + "bone.ply"}, draw_mesh = "Skin", title = "Rough Cut", base_filename = skin_file[:-8])
    app.MainLoop()
    del frame
    del app
