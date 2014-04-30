
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
A GUI tool for highlighting mesh errors for debug purposes.
'''

from settings import *

from OpenGL.GL import *
from OpenGL.GLUT import *
from math import pi, acos

from gui_tool import GuiTool

COLOURS = {"red": (1,0.2,0.2), "green": (0.2, 1,0.2), "blue":(0.2,0.2,1),}

class DebugTool(GuiTool):

    def __init__(self, name):
        super(DebugTool, self).__init__(name)

        self.line_list = {}
        self.thickness = 0.1
        self.colour = "green"
        self.mode = -1

    def initDisplay(self):
        for name, mesh in self.controller.meshes.items():

            # find all edges with less than two associated faces
            edges = []
            for e in mesh.edges.itervalues():
                if e.lface is None or e.rface is None:
                    edges.append(e)

            if not edges:
                continue

            self.line_list[name] = glGenLists(1)
            glNewList(self.line_list[name], GL_COMPILE)
            glColor3f(*COLOURS[self.colour])
            for e in edges:
                dl = e.displacement()
                start = e.v2
                end = e.v1
                dx = dl[0] #start[0] - end[0]
                dy = dl[1] #start[1] - end[1]
                dz = dl[2] #start[2] - end[2]
                length_d = dl.magnitude()
                if length_d > 0:
                    #axis of rotation = (0, 0, 1) cross (dx, dy, dz) = (-dy, dx, 0)
                    #angle to rotate = 180.0 / pi * acos((0,0,1).(dx, dy, dz) / (dx, dy, dz).(dx, dy, dz))
                    glPushMatrix()
                    glTranslatef(start[0], start[1], start[2])
                    glRotatef(180.0 / pi * acos(dz / length_d), -dy, dx, 0)
                    glutSolidSphere(2 * self.thickness, 10, 10)
                    glutSolidCylinder(2 * self.thickness, -length_d, 20 ,20)
                    glPopMatrix()
            glEndList()
        
    def getSubTools(self):
        return ["Highlight", "Show errors"]

    def select(self, subtool):
        self.mode = subtool

        if subtool == 1:
            self.controller.Refresh()

    def getDisplayObjects(self):

        if self.mode != 1:
            return {}

        objs = {}
    
        for key in self.controller.meshes.keys():
            if key in self.line_list:
                objs[key+"_lines"] = {}
                objs[key+"_lines"]["matrix_mode"] = GL_MODELVIEW
                objs[key+"_lines"]["style"] = "Red"
                objs[key+"_lines"]["visible"] = True
                objs[key+"_lines"]["list"] = self.line_list[key]

        return objs

    def OnMouseMotion(self, x, y, lastx, lasty, event):

        if self.mode == 0:
            return self.highlight()
        elif self.mode == 1:
            return False

    def highlight(self):
        for mesh in self.controller.meshes.keys():
            if not self.controller.meshes.visible[mesh]:
                continue
            face_hit = self.controller.hit_location(mesh)
            if face_hit:
                x,y,z,name = face_hit
                self.controller.view.highlight = True
                self.controller.view.highlight_index = name*3

                return True

        self.controller.view.highlight = None
        return False

