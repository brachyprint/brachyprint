
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


from __future__ import division
from settings import *

import wx


class WizardPage(wx.Panel):
    """A text control containing clickable areas with associated handler.
    """

    def __init__(self, parent, description, *args, **kw):
        super(WizardPage, self).__init__(parent, *args, **kw)

        # create a text control to display the description
        self.textctrl = wx.TextCtrl(self,5, "",wx.Point(20,20), wx.Size(200,400), \
                wx.BORDER_NONE | wx.TE_MULTILINE |  wx.TE_READONLY)# |  wx.TE_RICH2)

        self.SetBackgroundColour(parent.GetDefaultAttributes().colBg)
        self.textctrl.SetBackgroundColour(parent.GetDefaultAttributes().colBg)

        # go through ``description'', adding each list item to the text control
        # with the desired attributes
        self.text = ""
        start = 0
        self.ranges = []
        self.handlers = []

        default = wx.TextAttr()
        for part in description:
            style, text, handler = part
            if not style:
                style = default
            self.textctrl.SetDefaultStyle(style)
            self.textctrl.AppendText(text)

            # save the text
            self.text += text
            self.ranges.append((start, start+len(text)-1))
            start += len(text)
            self.handlers.append(handler)

        # bind the mouse motion/click handlers
        self.textctrl.Bind(wx.EVT_LEFT_UP, self.onLeftUp)
        self.textctrl.Bind(wx.EVT_MOTION, self.onMotion)


    def onLeftUp(self, evt):
        # if there is a click handler for the text under the mouse,
        # invoke it
        position = evt.GetPosition()
        (res,hitpos) = self.textctrl.HitTestPos(position)

        for i, r in enumerate(self.ranges):
            if hitpos >= r[0] and hitpos <= r[1]:
                handler = self.handlers[i]
                if handler:
                    handler(evt)

                return


    def onMotion(self, evt):
        # if there is a click handler for the text under the mouse,
        # switch the cursor to a hand
        position = evt.GetPosition()
        (res,hitpos) = self.textctrl.HitTestPos(position)

        for i, r in enumerate(self.ranges):
            if hitpos >= r[0] and hitpos <= r[1]:
                if self.handlers[i]:
                    cursor = wx.StockCursor(wx.CURSOR_HAND)
                    self.textctrl.SetCursor(cursor)
                    return
                break

        cursor = wx.StockCursor(wx.CURSOR_ARROW)
        self.textctrl.SetCursor(cursor)


class WizardPanel(wx.Panel):
    """A wx panel to guide the user through the mask making flow.
    """

    def __init__(self, parent, controller, *args, **kw):
        super(WizardPanel, self).__init__(parent, *args, **kw) 
        self.parent = parent
        self.controller = controller
        self._initUI()


    def getOnChangedHandler(self, tool, subtool):
        def OnChanged(event):
            self.controller.selectTool(tool, subtool)
        return OnChanged


    def _initUI(self):

        panel = wx.Panel(self)

        self.nb = wx.Notebook(panel)
 
        # create the page windows as children of the notebook
        page1 = WizardPage(self.nb, [(None, "Welcome to MaskMaker!\n\nThe first step is to load some scan data to use as a basis for the mask. Either\n\n", None),
                                     (wx.TextAttr("blue"), "Process and import CT data", lambda x: self.parent.OnImport(x)),
                                     (None, "\n\nor\n\n", None),
                                     (wx.TextAttr("blue"), "Open an existing processed file", lambda x: self.parent.OnOpen(x))])
        page2 = WizardPage(self.nb, [(None, "Draw a region of interest to define the coarse mask outline.", None),
                                     (None, "\n\nThen select the region and apply an extrusion.", None)])
        page3 = WizardPage(self.nb, [(None, "Page3", None)])
 
        # add the pages to the notebook with the label to show on the tab
        self.nb.AddPage(page1, "Import")
        self.nb.AddPage(page2, "Coarse selection")
        self.nb.AddPage(page3, "Fine selection")
 
        # finally, put the notebook in a sizer for the panel to manage
        # the layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.nb, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        panel.SetAutoLayout(True)
        panel.Layout()

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(panel, 1, wx.EXPAND | wx.ALL, 5)

        # XXX: next/back buttons; are they needed?
        #self.next_button = wx.Button(self, label="Next >")
        #self.back_button = wx.Button(self, label="< Back")

        #buttonbox = wx.BoxSizer(wx.HORIZONTAL)
        #buttonbox.Add(self.back_button, 0, wx.EXPAND)
        #buttonbox.Add(self.next_button, 0, wx.EXPAND)
        #box.Add(buttonbox, 0, wx.EXPAND)

        self.SetSizer(box)


    def ChangeSelection(self, page):
        self.nb.ChangeSelection(page)


