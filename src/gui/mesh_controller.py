
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
A controller class to use in conjuction with a MeshCanvas view.
'''

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import mesh
from mesh import Vector

from gui import RoiGUI
from settings import *

from mesh_display import MeshCollectionDisplay


class opengl_list:
    def __init__(self, list_):
        self.list = list_
    def __call__(self):
        glCallList(self.list)


class renderOneBlock:
    """A volume is split into multiple blocks, each containing BLOCKSIZE triangles"""
    def __init__(self, block_name, mesh):
        self.block_name = block_name
        self.mesh = mesh
    def __call__(self):
        for f in self.mesh.faces[self.block_name * BLOCKSIZE: (self.block_name+1) * BLOCKSIZE]:
            glPushName(f.name)
            glBegin(GL_TRIANGLES)
            assert len(f.vertices) == 3
            for v in f.vertices:
                n = v.normal()
                glNormal3f(n.x, n.y, n.z)
                glVertex(v.x, v.y, v.z)
            glEnd()
            glPopName()


class ViewPort(object):
    def __init__(self):
        self.scale = 0.5
        self.theta = 180
        self.phi = 0

        self.width = 0
        self.height = 0

        self.tx = 0
        self.ty = 0
        self.tz = 0

        self.range_max = 0

    def setSize(self, size):
        self.width = size.width
        self.height = size.height

    def xscale(self):
        if self.width > self.height:
            return self.scale * self.width / self.height
        else:
            return self.scale

    def yscale(self):
        if self.width > self.height:
            return self.scale
        else:
            return self.scale * self.height / self.width


class MeshController(object):

    def __init__(self, view, meshes):

        # the associated MeshCanvas widget (`view')
        self.view = view

        # the associated mesh objects (`model')
        self.meshes = MeshCollectionDisplay(meshes)

        self.tools = {}
        self.currentTool = None

        self.band = []

        # initial mouse position
        self.lastx = self.x = 0
        self.lasty = self.y = 0

        self.viewport = ViewPort()
        self.view.viewport = self.viewport
        self.viewport.range_max = self.meshes.range_max()

    def addMesh(self, mesh, name):
        self.meshes.add_mesh(mesh)
        self.viewport.range_max = self.meshes.range_max()

    def InitGL(self):

        for tool in self.tools.values():
            tool.initDisplay()

        self.viewport.tx, self.viewport.ty, self.viewport.tz = -self.meshes.meanx(), -self.meshes.meany(), -self.meshes.meanz()

        self.Refresh()

    def draw(self):

        objs = self.meshes.get_display_objects()

        for tool in self.tools.values():
            obj = tool.getDisplayObjects()
            objs.update(obj)

        self.objs = objs

        self.view.displayObjects = objs

    def hit_location(self, meshname):
        winX = self.x
        winY = self.viewport.height - self.y

        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)

        # find the projection of the mouse point at the front of the viewport...
        x, y, z = gluUnProject(winX, winY, 0.0, modelview, projection, viewport)
        # ...and the back of the viewport
        x2, y2, z2 = gluUnProject(winX, winY, 1.0, modelview, projection, viewport)

        p = [Vector(x,y,z), Vector(x2,y2,z2)]

        intersects = []
        

        self.meshes[meshname].ensure_fresh_octrees() #Nb. Octrees should be fresh already
        for (ref_point, extends, face) in self.meshes[meshname].face_octree.intersect_with_line(p[0],p[1] - p[0], positive=False):
            # attempt to intersect the ray and the face
            ret = mesh.triangle_segment_intersect(p, face.vertices, 2)

            if isinstance(ret, mesh.Vector):
                intersects.append(((ret-Vector(x,y,z)).magnitude(), face, ret))

        if intersects:
            # sort the intersections in order of distance
            intersects = sorted(intersects, key=lambda x: x[0])
            ret = intersects[0][2]
            return (ret.x, ret.y, ret.z, intersects[0][1].name)

        return None


    def setVisible(self, name, value):
        self.meshes.setVisible(name, value)

    def setVerticesVisible(self, name, value):
        self.meshes.setVerticesVisible(name, value)

    def setStyle(self, name, value):
        self.meshes.setStyle(name, value)

    def Refresh(self):
        self.draw()
        self.view.Refresh()

    def addTool(self, tool):
        name = tool.name
        self.tools[name] = tool
        tool.setController(self)

    def selectTool(self, name, subtool=0):
        if self.currentTool:
            self.currentTool.deselect()
        self.currentTool = self.tools[name]
        self.currentTool.select(subtool)

    def getToolList(self):
        return self.tools.keys()

    def OnKeyPress(self, event):
        """Receive keypress events from the view.
        """
        keycode = event.GetKeyCode()

        if self.currentTool:
            try:
                return self.currentTool.OnKeyPress(keycode, event)
            except AttributeError:
                pass

    def OnSize(self, event):
        size = self.view.GetClientSize()
        self.viewport.setSize(size)

        self.view.updateViewPort()

    def updateView(self):
        self.view.updateViewPort()

    def OnMouseWheel(self, event):
        """Receive mousewheel events from the view.
        """
        if event.GetWheelRotation() < 0:
            self.viewport.scale *= 1.1 # = self.scale * 1.1 # ** (self.y - self.lasty)
        else:
            self.viewport.scale /= 1.1 # = self.scale * 0.9 # ** (self.y - self.lasty)
        self.updateView()
        return True

    def OnMouseDown(self, event):

        self.x, self.y = self.lastx, self.lasty = event.GetPosition()

        if self.currentTool:
            try:
                return self.currentTool.OnMouseDown(self.x, self.y, self.lastx, self.lasty, event)
            except AttributeError:
                pass

    def OnMouseUp(self, event):

        if self.currentTool:
            try:
                return self.currentTool.OnMouseUp(event)
            except AttributeError:
                pass

        # TODO:
        mode = ("", "")
        if mode == "Rubber Band" and self.sphere_selection is not None:
            self.placeSphere(int(self.sphere_selection))
            self.compile_band()
            self.sphere_selection = None
            return True

    def OnMouseMotion(self, event):
        self.lastx, self.lasty = self.x, self.y
        self.x, self.y = event.GetPosition()

        if self.currentTool:
            try:
                return self.currentTool.OnMouseMotion(self.x, self.y, self.lastx, self.lasty, event)
            except AttributeError:
                pass
        

        if event.Dragging() and event.LeftIsDown():
            # TODO
            mode = ("", "")
            if mode == "Rubber Band" and self.sphere_selection is not None:
                self.placeSphere(int(self.sphere_selection))
                self.compile_band()
            return True


