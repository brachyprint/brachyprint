
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


class ModePanel(wx.Panel):
    """A wx panel to select the current tool.
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

