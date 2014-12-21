#!/usr/bin/env python

#    Brachyprint -- 3D printing brachytherapy moulds
#    Copyright (C) 2013-14  Martin Green and Oliver Madge
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

from wx import xrc

from settings import *
import mesh
from octrees import Octree
from points import expand, make_ply

from gui import MeshCanvas
from gui import MeshController
from gui import ThreadProgressDialog

from gui.tools import RotateTool, ZoomTool, RoiTool, SelectTool
from gui.panels import MeshPanel, WizardPanel
from gui.dialogs import ImportDialog


class MouldMakerApp(wx.App):
    """MouldMaker application class.
    """
 
    def OnInit(self):
        self.res = xrc.XmlResource('gui/res/menu.xrc')
        self.init_frame()
        return True

    def init_frame(self):
        # initialise the menu bar
        self.menubar = self.res.LoadMenuBar("menu_bar")
        self.frame = MainWindow(title="MouldMaker", menubar=self.menubar)

        self.frame.Bind(wx.EVT_MENU, self.frame.OnOpen, id=xrc.XRCID("wxID_OPEN"))
        self.frame.Bind(wx.EVT_MENU, self.frame.OnSave, id=xrc.XRCID("wxID_SAVE"))
        self.frame.Bind(wx.EVT_MENU, self.frame.OnImport, id=xrc.XRCID("wxID_IMPORT"))
        self.frame.Bind(wx.EVT_MENU, self.frame.OnExit, id=xrc.XRCID("wxID_EXIT"))

        self.frame.Bind(wx.EVT_MENU, self.frame.OnResetView, id=xrc.XRCID("wxID_RESET_VIEW"))
        self.frame.Bind(wx.EVT_MENU, self.frame.OnShowGrid, id=xrc.XRCID("wxID_SHOW_GRID"))
        self.frame.Bind(wx.EVT_MENU, self.frame.OnScreenshot, id=xrc.XRCID("wxID_SCREENSHOT"))

        self.frame.Bind(wx.EVT_MENU, self.frame.OnAbout, id=xrc.XRCID("wxID_ABOUT"))

        self.frame.Show()


class Mode(object):
    """Class to store the current application mode.
    """

    def __init__(self):
        self.loaded = False
        self.complete_roi = False


class MainWindow(wx.Frame):

    def __init__(self, parent = None, id = -1, title = "MouldMaker", rois = {}, meshes={}, menubar=None, tools=[RotateTool("Rotate"), ZoomTool("Zoom"), SelectTool("Select")]):
        # Init
        super(MainWindow, self).__init__(
                parent, id, title, size = (1024,768),
                style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE
        )

        self.mode = Mode()

        rois = {"Lasso": {"meshname": "Skin",
                            "closed": True,
                            "colour": "red",
                         "thickness": 1,
                          "onSelect": None }}

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

        # build the toolbar
        self.toolbar = wx.ToolBar(self)

        select_tool = lambda name: lambda evt: self.SelectTool(name)

        self.tools = [{"id": -1, "name":  "import", "type": "label", "icon": wx.Bitmap('gui/icons/icon-import.png'), "onSelect": self.OnImport},
                      {"id": -1, "name":    "open", "type": "label", "icon": wx.Bitmap('gui/icons/icon-open.png'), "onSelect": self.OnOpen},
                      {"id": -1, "name":    "save", "type": "label", "icon": wx.Bitmap('gui/icons/icon-save.png'), "onSelect": self.OnSave},
                      {"id": -1, "name":    "sep1", "separator": True},
                      {"id": -1, "name":  "rotate", "type": "radio", "icon": wx.Bitmap('gui/icons/icon-pan.png'), "onSelect": select_tool("Rotate")},
                      {"id": -1, "name":    "zoom", "type": "radio", "icon": wx.Bitmap('gui/icons/icon-zoom.png'), "onSelect": select_tool("Zoom")},
                      {"id": -1, "name":   "lasso", "type": "radio", "icon": wx.Bitmap('gui/icons/icon-lasso.png'), "onSelect": select_tool("Lasso")},
                      {"id": -1, "name":  "select", "type": "radio", "icon": wx.Bitmap('gui/icons/icon-select.png'), "onSelect": select_tool("Select")},
                      {"id": -1, "name": "extrude", "type": "radio", "icon": wx.Bitmap('gui/icons/icon-extrude.png'), "onSelect": select_tool("Extrude")},
                      {"id": -1, "name":    "sep2", "separator": True},
                      {"id": -1, "name":  "export", "type": "radio", "icon": wx.Bitmap('gui/icons/icon-export.png'), "onSelect": self.OnExport}]

        for i, tool in enumerate(self.tools):
            if "separator" in tool:
                self.toolbar.AddSeparator()
            else:
                new_id = wx.NewId()
                self.tools[i]["id"] = new_id
                icon = self.tools[i]["icon"]
                name = self.tools[i]["name"]

                if tool["type"] == "radio":
                    otool = self.toolbar.AddRadioTool(new_id, icon)
                elif tool["type"] == "label":
                    otool = self.toolbar.AddLabelTool(new_id, name, icon)

                self.Bind(wx.EVT_TOOL, tool["onSelect"], otool)
                self.toolbar.EnableTool(new_id, False)

        # create toolbar
        self.toolbar.Realize()

        # create the panels to select the mesh options and the GUI tool
        self.meshPanel = MeshPanel(self, self.meshController, meshes.keys(), style=wx.SUNKEN_BORDER)
        self.wizardPanel = WizardPanel(self, self.meshController)

        # layout the GUI
        box = wx.FlexGridSizer(2, 2)

        box.AddGrowableCol(1, 1)
        box.AddGrowableRow(1, 1)

        vbox = wx.BoxSizer(wx.VERTICAL)
        box.Add((0,0), 0)
        box.Add(self.toolbar, 0, wx.EXPAND)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.meshPanel, 0, wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.wizardPanel, 0.5, wx.EXPAND)

        box.Add(vbox, 0, wx.EXPAND)

        vbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(self.meshCanvas, 1, wx.EXPAND)
        box.Add(vbox, 1, wx.EXPAND)

        self.meshPanel.parent = self.meshController

        overall = wx.BoxSizer(wx.VERTICAL)
        overall.Add(box, 1, wx.EXPAND | wx.ALL, border=5)

        self.SetAutoLayout(True)
        self.SetSizer(overall)
        self.Layout()

        # StatusBar
        #self.CreateStatusBar()

        # create the Menubar
        self.menubar = menubar
        if self.menubar:
            self.SetMenuBar(self.menubar)

        # show
        self.Show(True)

        # maximise the window
        self.Maximize()

        # select the rotate tool
        self.SelectTool('Rotate')

        # enable the correct tools for the current mode
        self.EnableTools()


    def SelectTool(self, name):
        self.meshController.selectTool(name)


    def UpdateMode(self):
        self.mode.complete_roi = False

        class Complete(Exception): pass
        try:
            for meshname in self.meshController.meshes.rois.keys():
                for roi in self.meshController.meshes.rois[meshname]:
                    if roi.is_complete():
                        self.mode.complete_roi = True
                        raise Complete
        except Complete:
            pass

        self.EnableTools()
        self.SelectWizardPage()


    def EnableTools(self):
        """Enable the tools appropriate to the current mode.
        """

        enables = {}
        for key in ["import", "open"]:
            enables[key] = True

        # enable the pan/zoom and lasso tools
        for key in ["save", "rotate", "zoom", "lasso"]:
            enables[key] = self.mode.loaded

        # enable the "select" tool when a lasso is drawn
        enables["select"] = self.mode.complete_roi

        # apply enables/disables to the toolbar
        for tool in self.tools:
            if tool["name"] in enables:
                if enables[tool["name"]]:
                    self.toolbar.EnableTool(tool["id"], True)
                else:
                    self.toolbar.EnableTool(tool["id"], False)


    def SelectWizardPage(self):
        if not self.mode.loaded:
            self.wizardPanel.ChangeSelection(0)
        else:
            self.wizardPanel.ChangeSelection(1)


    def warn(self, msg):
        dlg = wx.MessageDialog(self, msg, "Mouldmaker", wx.YES_NO | wx.ICON_QUESTION)
        ret = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        return ret


    def Refresh(self):
        self.meshController.Refresh()
        self.EnableTools()


    def OnImport(self, event):
        dialog = ImportDialog(None)

        # XXX: this is not working as a modal dialog in Ubuntu 14.04
        #      Fsking Ubuntu -- see http://trac.wxwidgets.org/ticket/14855
        #      Running with LIBOVERLAY_SCROLLBAR=0 fixes the problem...
        if dialog.ShowModal() == wx.ID_CANCEL:
            dialog.Destroy()
            return

        # TODO: retrieve the address of the data to import from the dialog

        print dialog.dirs.GetPath()
        print dialog.series[dialog.series_list.GetFirstSelected()]

        dialog.Destroy()


    def OnSave(self, event):
        self.warn("Save not implemented yet. OK?")


    def OnOpen(self, event):

        if self.mode.loaded and not self.warn("Model already loaded. Replace?"):
            return

        openFileDialog = wx.FileDialog(self, "Load", DEFAULT_OUTPUT_DIR, DEFAULT_OUTPUT_FILE, wildcard="*.skin.ply")
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            openFileDialog.Destroy()
            return

        skin_file = openFileDialog.GetPath()
        openFileDialog.Destroy()
        base_filename = skin_file[:-8]

        #ply_files = {"Skin": skin_file, "Bone": base_filename + "bone.ply"}
        ply_files = {"Skin": skin_file}

        def done():
            self.Refresh()

            # populate the mesh info panel
            self.meshPanel.clear()
            for name in ply_files.keys():
                self.meshPanel.addMesh(name)
            self.Refresh()


        def import_files():
            j = 0
            reader = mesh.fileio.PlyReader()
            for name, filename in ply_files.items():
                m = mesh.Mesh()
                for i in reader.read_part(m, filename):
                    yield int((i + j*10)/len(ply_files))
                m.ensure_fresh_octrees()
                self.meshController.addMesh(m, name, clear=(j==0), reset=True) # clear when adding first mesh
                j += 1

        # create a thread to manage the loading and display progress
        self.thread = ThreadProgressDialog(self, import_files, "Loading scan data...", done)
        self.thread.start()

        self.mode.loaded = True


    def OnExport(self, event):
        pass


    def OnExit(self, event):
        self.Close(True) # Close the frame.


    def OnResetView(self, event):
        self.meshController.resetViewPort()
        self.Refresh()


    def OnShowGrid(self, event):

        item = self.GetMenuBar().FindItemById(xrc.XRCID('wxID_SHOW_GRID'))

        self.meshController.showGrid(item.IsChecked())

        self.Refresh()


    def OnScreenshot(self, event):
        self.meshCanvas.Screenshot("screenshot.jpg", wx.BITMAP_TYPE_JPEG)


    def OnAbout(self, event):
        message = "Brachyprint mould editor"
        caption = "MouldMaker"
        wx.MessageBox(message, caption, wx.OK)


if __name__ == '__main__':
    # create a mouldmaker wx application
    app = MouldMakerApp(False)

    # run the main loop
    app.MainLoop()

    # delete the app if the main loop returns, to ensure program exits cleanly
    del app


