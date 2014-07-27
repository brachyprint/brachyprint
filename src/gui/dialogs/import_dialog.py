
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

import os
import dicom

import numpy

import PIL.Image


class BorderFrameCtrl(wx.Panel):
    def __init__(self, parent, id, title, style=wx.NO_BORDER):
        wx.Panel.__init__(self, parent, id=-1,)

        self.ctrl = None

        self.title = wx.StaticText(self, -1, title, pos=(7, 4))

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE,self.OnSize)

    def SetChild(self, ctrl):
        self.ctrl = ctrl

    def OnSize(self, event):
        if self.ctrl:
            size = event.GetSize()
            title_size = self.title.GetSize()
            h = title_size.y + 4 + 4 + 2
            self.ctrl.SetPosition((1,1+h))
            self.ctrl.SetSize((size.x-2,size.y-2-h))
            try:
                self.ctrl.SetColumnWidth(0, size.x-2)
            except AttributeError: # child does not have the SetColumnWidth method
                pass
        event.Skip()

    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.SetBackground(wx.Brush(wx.Colour(196,193,189)))
        dc.Clear()
        size = self.GetSize()
        gc = wx.GraphicsContext.Create(dc)

        title_size = self.title.GetSize()
        h = title_size.y + 4 + 4
        grad = gc.CreateLinearGradientBrush(1,1, 1, h, wx.Colour(254,254,254), wx.Colour(241,240,238))
        gc.SetBrush(grad)
        gc.DrawRectangle(1, 1, size.x-2, h)
        gc.SetBrush(wx.Brush(wx.Colour(174,170,166)))
        gc.DrawRectangle(1, h+1, size.x-2, 1)
        gc.SetBrush(wx.Brush(wx.Colour(242,241,240)))
        gc.DrawRectangle(1, h+2, size.x-2, 1)


class DicomPreviewPanel(wx.Panel):
    def __init__(self,parent, id, style=wx.NO_BORDER):
        wx.Panel.__init__(self, parent, id=-1,)
        self.filename = None
        self.bitmap = None
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        # TODO: add more windows, e.g.
        #         * lung: 1200  600
        #         * bone: 1024 1500
        #         * fat:   400 1000
        self.window = 400
        self.level = 1000

    def setFilename(self, filename):
        self.filename = filename
        self.loadBitmap()
        self.Refresh()

    def loadBitmap(self):
        if self.filename is not None:
            d = dicom.read_file(self.filename)

            try:
                data = d.pixel_array
            except TypeError: # no pixel data
                # XXX: display a checker board pattern or something?
                self.bitmap = None
                return
            except NotImplementedError: # DICOM doesn't support the pixel data
                self.bitmap = None
                return

            #zoom_level = z - ceil(log(max(data.shape) / float(TILE_SIZE), 2))
            #tile_data_size = TILE_SIZE * 2 ** -zoom_level
            #tile_data = data[x * tile_data_size: (x + 1) * tile_data_size, y * tile_data_size: (y + 1) * tile_data_size]

            # window the scan data
            windowed_data = numpy.piecewise(data,
                        [data <= (self.level - 0.5 - (self.window - 1) / 2),
                         data > (self.level - 0.5 + (self.window - 1) / 2)],
                        [0, 255, lambda x: ((x - (self.level - 0.5)) / (self.window - 1) + 0.5) * (255 - 0)])

            # get the display size
            (w, h) = self.GetSize()

            # resize the scan data
            img = PIL.Image.fromarray(numpy.uint8(windowed_data)).resize((w, h), PIL.Image.ANTIALIAS)

            # create a blank image and blat the scan data onto it
            image = wx.EmptyImage(w, h)
            image.SetData(img.convert('RGB').tostring())
            self.bitmap = image.ConvertToBitmap()
        else:
            self.bitmap = None

    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.SetBackground(wx.Brush(wx.Colour(196,193,189)))
        dc.Clear()

        if self.bitmap:
            dc.DrawBitmap(self.bitmap, 0, 0)

class ImportDialog(wx.Dialog):
    """A wx dialog to import CT scan data.
    """
    def __init__(self, *args, **kw):

        super(ImportDialog, self).__init__(None, -1, "Import CT data", wx.DefaultPosition, wx.Size(640, 500))

        default_dir = os.path.normpath(os.path.join(os.getcwd(), DEFAULT_INPUT_DIR))
        dirs_panel = BorderFrameCtrl(self, -1, "Directory")
        self.dirs = wx.GenericDirCtrl(dirs_panel, -1, default_dir, style=wx.DIRCTRL_DIR_ONLY | wx.BORDER_NONE)#, size=(200,225))
        dirs_panel.SetChild(self.dirs)

        series_panel = BorderFrameCtrl(self, -1, "Series")

        self.series_list = wx.ListCtrl(series_panel, -1, style=wx.LC_SINGLE_SEL|wx.LC_REPORT|wx.LC_NO_HEADER)

        series_panel.SetChild(self.series_list)

        self.series_list.InsertColumn(0, "Series")

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.box = wx.BoxSizer(wx.HORIZONTAL)

        self.box.Add(dirs_panel, 1, wx.EXPAND | wx.RIGHT, border=10)

        preview_panel = BorderFrameCtrl(self, -1, "Preview")
        self.preview = DicomPreviewPanel(preview_panel, -1)
        preview_panel.SetChild(self.preview)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(series_panel, 1, wx.EXPAND)
        box.Add(preview_panel, 2, wx.EXPAND | wx.TOP, border=10)

        self.box.Add(box, 2, wx.EXPAND)

        # directory change event
        self.dirs.Bind(wx.EVT_TREE_SEL_CHANGED, self.DirChanged)

        # series selection change event
        self.series_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.SeriesSelected)

        self.vbox.Add(self.box, 1, wx.EXPAND | wx.ALL, border=10)

        hbox_buttons = wx.BoxSizer(wx.HORIZONTAL)
        btn_cancel = wx.Button(self, wx.ID_ANY, "Cancel")

        btn_cancel.Bind(wx.EVT_BUTTON, self.OnCancel)

        hbox_buttons.Add(btn_cancel, 0);

        self.btn_import = wx.Button(self, wx.ID_ANY, "Import")
        self.btn_import.SetDefault()
        self.btn_import.Disable()

        hbox_buttons.Add(self.btn_import, 0, wx.LEFT | wx.BOTTOM, 5)
        self.vbox.Add(hbox_buttons, 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, 10)

        self.SetAutoLayout(True)
        self.SetSizer(self.vbox)
        self.Layout()


    def OnCancel(self, evt):
        self.Destroy()

    def DirChanged(self, evt):
        '''Selected directory has changed, so update the series list.
        '''

        path = self.dirs.GetPath()

        # clear the preview
        self.preview.setFilename(None)

        # ensure the import button is disabled
        self.btn_import.Disable()

        seriesInstanceUIDs = {}

        # attempt to read all the files in the current directory
        for f in os.listdir(path):
            filepath = os.path.join(path,f)
            if os.path.isfile(filepath):
                try:
                    d = dicom.read_file(filepath)
                except dicom.filereader.InvalidDicomError: # ignore invalid DICOM files
                    continue
                try:
                    uid = d.SeriesInstanceUID
                except AttributeError:
                    uid = "default"
                if uid in seriesInstanceUIDs:
                    seriesInstanceUIDs[uid]["files"].append(filepath)
                else:
                    try:
                        study_desc = d.StudyDescription
                    except AttributeError:
                        study_desc = ''
                    try:
                        series_desc = d.SeriesDescription
                    except AttributeError:
                        series_desc = ''
                    try:
                        modality = d.Modality
                    except AttributeError:
                        modality = ''
                    try:
                        patients_name = d.PatientsName
                    except AttributeError:
                        patients_name = ''
                    description = "%s - %s - %s - %s" % (modality, patients_name, study_desc, series_desc)
                    seriesInstanceUIDs[uid] = {"description": description, "files": [filepath]}
                del d

        self.series = seriesInstanceUIDs.items()

        # clear the series selection listbox
        self.series_list.DeleteAllItems()

        # add each series to it
        i = 0
        for s in self.series:
            self.series_list.InsertStringItem(i, s[1]["description"])
            if i % 2:
                self.series_list.SetItemBackgroundColour(i, wx.Color(221, 221, 221))
            else:
                self.series_list.SetItemBackgroundColour(i, wx.Color(238, 238, 238))
            i = i + 1


    def SeriesSelected(self, evt):
        series = self.series[self.series_list.GetFirstSelected()]

        self.preview.setFilename(series[1]["files"][0])

        # enable the import button
        self.btn_import.Enable()

