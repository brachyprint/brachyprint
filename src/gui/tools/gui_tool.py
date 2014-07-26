
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


'''
A base class to extend for GUI tools.
'''


class GuiTool(object):

    def __init__(self, name):
        self.controller = None
        self.name = name

    def setController(self, controller):
        self.controller = controller

    def initDisplay(self):
        pass

    def getSubTools(self):
        return [self.name]

    def select(self, subtool):
        pass

    def deselect(self):
        pass

    def getDisplayObjects(self):
        return {}

    def OnKeyPress(self, keycode, event):
        pass

    def OnMouseDown(self, x, y, lastx, lasty, event):
        pass

    def OnMouseUp(self, event):
        pass

    def OnMouseMotion(self, x, y, lastx, lasty, event):
        pass

