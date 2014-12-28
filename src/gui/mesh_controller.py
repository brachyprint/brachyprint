
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


'''
A controller class to use in conjuction with a MeshCanvas view.
'''

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import mesh
from mesh import Vector
from mesh import plane

from gui import RoiGUI
from settings import *

from mesh_display import MeshCollectionDisplay


class ViewPort(object):
    """Representation of a viewport onto a display.
    """

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

    def __init__(self, parent, view, meshes, vertex_size = 3):

        # the parent application
        self.parent = parent

        # the associated MeshCanvas widget (`view')
        self.view = view

        # the associated mesh objects (`model')
        self.meshes = MeshCollectionDisplay(meshes, vertex_size = vertex_size)

        self.tools = {}
        self.currentTool = None

        self.band = []

        # grid off
        self.showgrid = False

        # initial mouse position
        self.lastx = self.x = 0
        self.lasty = self.y = 0

        self.resetViewPort()
        #self.viewport = ViewPort()
        #self.view.viewport = self.viewport
        #self.viewport.range_max = self.meshes.range_max()


    def addMesh(self, m, name, clear=False, reset=False):
        if clear:
            self.meshes.clear()

        self.meshes.add_mesh(m, name)

        if reset:
            self.resetViewPort()


    def resetViewPort(self):
        self.viewport = ViewPort()
        size = self.view.GetClientSize()
        self.viewport.setSize(size)
        self.view.viewport = self.viewport
        self.viewport.range_max = self.meshes.range_max()
        self.viewport.tx, self.viewport.ty, self.viewport.tz = -self.meshes.meanx(), -self.meshes.meany(), -self.meshes.meanz()


    def updateView(self):
        self.view.updateViewPort()


    def Refresh(self):
        self.parent.UpdateMode()
        self.draw()
        #self.view.OnDraw()
        self.updateView()
        self.view.Refresh(False)


    def InitGL(self):
        """Initialise the OpenGL display.
        """

        for tool in self.tools.values():
            tool.initDisplay()

        self.viewport.tx, self.viewport.ty, self.viewport.tz = -self.meshes.meanx(), -self.meshes.meany(), -self.meshes.meanz()

        self.Refresh()


    def draw(self):
        """Collect display objects from all relevant GUI components (e.g. meshes, tools).
        """

        objs = self.meshes.get_display_objects()

        for tool in self.tools.values():
            obj = tool.getDisplayObjects()
            objs.extend(obj)

        self.objs = objs

        self.view.displayObjects = objs


    def hit_vector(self):
        """Return a list of Vectors representing the intersection of the current mouse position
        with the front and back of the viewing frustum.
        """
        winX = self.x
        winY = self.viewport.height - self.y

        # fetch the OpenGL transformation matrices
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)

        # XXX: gluUnProject is apparently deprecated, so this should be replaced with an
        #      explicit function

        # find the projection of the mouse point at the front of the viewport...
        x, y, z = gluUnProject(winX, winY, 0.0, modelview, projection, viewport)
        # ...and the back of the viewport
        x2, y2, z2 = gluUnProject(winX, winY, 1.0, modelview, projection, viewport)

        # construct the line between the front and back of the viewport
        return [Vector(x,y,z), Vector(x2,y2,z2)]


    def hit_mesh(self, meshname):
        """Determine coordinates of the intersection between the current
        mouse coordinates and a mesh.
        """

        # get the frustum intersection vector, and deconstruct it
        p = self.hit_vector()
        x,y,z = p[0].x, p[0].y, p[0].z
        x2,y2,z2 = p[1].x, p[1].y, p[1].z

        intersections = []

        # use octrees to get a list of faces with possible intersections
        for f in self.meshes[meshname].get_face_octree().intersect_with_line((x,y,z),(x2-x,y2-y,z2-z)):
            # extract the Face object
            face = f[2]

            # attempt to intersect the ray and the face
            ret = mesh.triangle_segment_intersect(p, face.vertices, 2)

            # add intersections to the list
            if isinstance(ret, mesh.Vector):
                intersections.append(((ret-Vector(x,y,z)).magnitude(), face, ret))

        if intersections:
            # sort the intersections in order of distance
            intersections = sorted(intersections, key=lambda x: x[0])

            # return the one closest to the front of the viewport
            ret = intersections[0][2]
            return (ret.x, ret.y, ret.z, intersections[0][1].name)

        # no intersection
        return None


    def hit_roi(self, roi):
        """Determine coordinates of the intersection between the current
        mouse coordinates and an ROI.
        """

        # get the frustum intersection vector, and deconstruct it
        v = self.hit_vector()
        l = [v[0], (v[1]-v[0]).normalise()]

        # test for the intersection of each point with the vector
        for i, p in enumerate(roi.points):
            (x, y, z, face_name) = p
            
            if plane.sphere_segment_intersect(Vector(x,y,z), 5*roi.thickness, l):
                # FIXME: will return the first found intersection, not necessarily
                #        the closest to the front of the viewport
                return (i, p)

        # no intersection
        return None


    def showGrid(self, show):
        self.showgrid = show


    def setVisible(self, name, value):
        self.meshes.setVisible(name, value)


    def setVerticesVisible(self, name, value):
        self.meshes.setVerticesVisible(name, value)


    def setStyle(self, name, value):
        self.meshes.setStyle(name, value)


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


    def OnSize(self, event):
        size = self.view.GetClientSize()
        self.viewport.setSize(size)

        self.view.updateViewPort()

        return True


    #########################################################################
    #                                                                       #
    # Event processing code                                                 #
    # =====================                                                 #
    #                                                                       #
    #  Standard pattern is to decode the event in the most useful fashion,  #
    #  then pass the decoded data and the event to the current tool.        #
    #                                                                       #
    #  Certain events, e.g. MouseWheel, and intercepted by the controller   #
    #  and handled directly here.                                           #
    #                                                                       #
    #########################################################################

    def OnKeyPress(self, event):
        """Receive keypress events from the view.
        """

        keycode = event.GetKeyCode()

        if self.currentTool:
            try:
                return self.currentTool.OnKeyPress(keycode, event)
            except NotImplementedError:
                pass


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
        """Receive mousedown events from the view.
        """

        self.x, self.y = self.lastx, self.lasty = event.GetPosition()

        if self.currentTool:
            try:
                return self.currentTool.OnMouseDown(self.x, self.y, self.lastx, self.lasty, event)
            except NotImplementedError:
                pass


    def OnMouseUp(self, event):
        """Receive mouseup events from the view.
        """

        if self.currentTool:
            try:
                return self.currentTool.OnMouseUp(event)
            except NotImplementedError:
                pass

        # TODO: ask Martin what this is supposed to do
        mode = ("", "")
        if mode == "Rubber Band" and self.sphere_selection is not None:
            self.placeSphere(int(self.sphere_selection))
            self.compile_band()
            self.sphere_selection = None
            return True


    def OnMouseMotion(self, event):
        """Receive mousemotion events from the view.
        """

        self.lastx, self.lasty = self.x, self.y
        self.x, self.y = event.GetPosition()

        if self.currentTool:
            try:
                return self.currentTool.OnMouseMotion(self.x, self.y, self.lastx, self.lasty, event)
            except NotImplementedError:
                pass

        # TODO: ask Martin what this is supposed to do
        if event.Dragging() and event.LeftIsDown():
            # TODO
            mode = ("", "")
            if mode == "Rubber Band" and self.sphere_selection is not None:
                self.placeSphere(int(self.sphere_selection))
                self.compile_band()
            return True

