
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
from gui import RoiGUI
from settings import *

# TODO:
import wx


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


class Range3d(object):
    def __init__(self, maxX, minX, maxY, minY, maxZ, minZ):
        self.max_X = maxX
        self.min_X = minX
        self.max_Y = maxY
        self.min_Y = minY
        self.max_Z = maxZ
        self.min_Z = minZ

    def rangex(self):
        return self.max_X - self.min_X

    def rangey(self):
        return self.max_Y - self.min_Y

    def rangez(self):
        return self.max_Z - self.min_Z

    def meanx(self):
        return (self.max_X + self.min_X) / 2

    def meany(self):
        return (self.max_Y + self.min_Y) / 2

    def meanz(self):
        return (self.max_Z + self.min_Z) / 2

    def range_max(self):
        return (self.rangex() ** 2 + self.rangey() ** 2 + self.rangez() ** 2) ** 0.5


class MeshCollection(Range3d):
    def __init__(self, d={}):
        self.meshes = d

        max_X = max([m.maxX for m in self.meshes.values()])
        min_X = min([m.minX for m in self.meshes.values()])
        max_Y = max([m.maxY for m in self.meshes.values()])
        min_Y = min([m.minY for m in self.meshes.values()])
        max_Z = max([m.maxZ for m in self.meshes.values()])
        min_Z = min([m.minZ for m in self.meshes.values()])

        super(MeshCollection, self).__init__(min_X, max_X, min_Y, max_Y, min_Z, max_Z)

    def items(self):
        return self.meshes.items()
    
    def keys(self):
        return self.meshes.keys()

    def add_mesh(self, m, name):
        self.meshes[name] = m
        self.max_X = max(self.max_X, m.maxX)
        self.min_X = min(self.min_X, m.minX)
        self.max_Y = max(self.max_Y, m.maxY)
        self.min_Y = min(self.min_Y, m.minY)
        self.max_Z = max(self.max_Z, m.maxZ)
        self.min_Z = min(self.min_Z, m.minZ)

    def __getitem__(self, it):
        return self.meshes[it]


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

    def __init__(self, view, meshes, rois, modePanel, meshPanel):

        # the associated MeshCanvas widget (`view')
        self.view = view

        # TODO: push into tools?
        self.modePanel = modePanel
        self.meshPanel = meshPanel

        # the associated mesh objects (`model')
        self.meshes = MeshCollection(meshes)

        self.mainList = {}
        self.vertexList = {}
        self.roiGUIs = {}
        for roiname, roi in rois.items():
            self.roiGUIs[roiname] = RoiGUI(mesh = self.meshes[roi["meshname"]], **roi)
        self.band = []

        # initial mouse position
        self.lastx = self.x = 0
        self.lasty = self.y = 0

        self.viewport = ViewPort()
        self.view.viewport = self.viewport
        self.viewport.range_max = self.meshes.range_max()

        #self.meshPanel.Bind(wx.EVT_COMBOBOX, self.meshPanelChange)
        #self.meshPanel.Bind(wx.EVT_CHECKBOX, self.meshPanelChange)

    def addMesh(self, mesh, name):
        self.meshes.add_mesh(mesh)
        self.viewport.range_max = self.meshes.range_max()

    def InitGL(self):
        for key, mesh in self.meshes.items():
            self.mainList[key] = self.faceListInit(mesh)
            self.vertexList[key] = self.vertexListInit(mesh)

        # TODO: push into tools
        for roiname, roigui in self.roiGUIs.items():
            roigui.InitGL()

        self.viewport.tx, self.viewport.ty, self.viewport.tz = -self.meshes.meanx(), -self.meshes.meany(), -self.meshes.meanz()

        self.draw()
        self.meshPanelChange()

    def draw(self):

        objs = {}

        for key, mesh in self.meshes.items():
            objs[key] = {}
            objs[key]["matrix_mode"] = GL_PROJECTION
            objs[key]["style"] = "Red"
            objs[key]["visible"] = True
            objs[key]["list"] = self.mainList[key]
            objs[key+"_vertices"] = {}
            objs[key+"_vertices"]["matrix_mode"] = GL_PROJECTION
            objs[key+"_vertices"]["style"] = "Red"
            objs[key+"_vertices"]["visible"] = True
            objs[key+"_vertices"]["list"] = self.vertexList[key]

        i = 0
        for roiGUI in self.roiGUIs.values():
            i+=1
            key = str(i)
            objs[key+"_spheres"] = {}
            objs[key+"_spheres"]["matrix_mode"] = GL_MODELVIEW
            objs[key+"_spheres"]["style"] = "Red"
            objs[key+"_spheres"]["visible"] = True
            objs[key+"_spheres"]["list"] = roiGUI.sphere_list
            objs[key+"_lines"] = {}
            objs[key+"_lines"]["matrix_mode"] = GL_MODELVIEW
            objs[key+"_lines"]["style"] = "Red"
            objs[key+"_lines"]["visible"] = True
            objs[key+"_lines"]["list"] = roiGUI.line_list
        #    glCallList(roiGUI.sphere_list)
        #    glCallList(roiGUI.line_list)

        self.objs = objs

        self.view.displayObjects = objs
        #self.view.OnPaint(None)
        #for roiname, roigui in self.roiGUIs.items():
        #    roigui.InitGL()
        
    def hit_location(self, meshname):
        #Find block
        hits = self.view.hit(self.x, self.y, opengl_list(self.mainList[meshname]), self.mainNumNames)
        if hits:
            x, y, z = gluUnProject(self.x, self.viewport.height - self.y, hits[0][0])
            #Find triangle
            hits = self.view.hit(self.x, self.y, renderOneBlock(hits[0][2][0], self.meshes[meshname]), BLOCKSIZE)
            return x, y, z, hits[0][2][0]

    def meshPanelChange(self):
        for k, v in self.meshPanel.visible.items():
            self.objs[k]["visible"] = v.GetValue()
        for k, v in self.meshPanel.vertices.items():
            self.objs[k+"_vertices"]["visible"] = v.GetValue()
        for k, v in self.meshPanel.cbs.items():
            self.objs[k]["style"] = v.GetValue()
        self.view.displayObjects = self.objs
        self.view.Refresh()

    def addTool(self, tool):
        pass

    def OnKeyPress(self, event):
        '''Receive keypress events from the view.
        '''
        keycode = event.GetKeyCode()

        # TODO: split this into the tool classes
        if keycode == wx.WXK_DELETE:
            mode = self.modePanel.GetMode()
            roiGUI = self.roiGUIs[mode[1]]
            if roiGUI.current_roi is not None and roiGUI.current_point_index is not None:
                if len(roiGUI.current_roi.points) == 1:
                    roiGUI.rois.remove(roiGUI.current_roi) 
                else:
                    roiGUI.current_roi.remove_point(roiGUI.current_point_index)
                roiGUI.current_roi = None
                roiGUI.current_point_index = None
                roiGUI.update()
                return True
        if keycode == wx.WXK_ESCAPE:
            mode = self.modePanel.GetMode()
            roiGUI = self.roiGUIs[mode[1]]
            roiGUI.current_roi = None
            roiGUI.current_point_index = None
            roiGUI.update()
            return True
        return False

    def OnSize(self, event):
        size = self.view.GetClientSize()
        self.viewport.setSize(size)

        self.view.updateViewPort()
        

    def updateView(self):
        self.view.updateViewPort()

    def OnMouseWheel(self, event):
        if event.GetWheelRotation() < 0:
            self.viewport.scale *= 1.1 # = self.scale * 1.1 # ** (self.y - self.lasty)
        else:
            self.viewport.scale /= 1.1 # = self.scale * 0.9 # ** (self.y - self.lasty)
        self.updateView()
        return True

    def OnMouseDown(self, event):

        self.x, self.y = self.lastx, self.lasty = event.GetPosition()

        mode = self.modePanel.GetMode()
        if event.LeftIsDown():
            if mode[0] == "Edit":
                roiGUI = self.roiGUIs[mode[1]]
                sphere_hits = self.view.hit(self.x, self.y, opengl_list(roiGUI.sphere_list), roiGUI.sphere_list_length())
                line_hits = self.view.hit(self.x, self.y, opengl_list(roiGUI.line_list), roiGUI.line_list_length())
                if sphere_hits:
                    sphereindex = None
                    for sphere_hit in sphere_hits:
                        if sphere_hit[2] != []:
                            sphere_index = sphere_hit[2][0]
                    roi, index =  roiGUI.pointlookup[sphere_index]
                    if roi == roiGUI.current_roi and \
                       roiGUI.current_roi.being_drawn() and \
                       ((roiGUI.current_point_index == 0 and roiGUI.current_roi.is_last(index)) or \
                        (roiGUI.current_roi.is_last(roiGUI.current_point_index) and index == 0)):
                        roiGUI.complete()
                    if roiGUI.current_roi == roi and roiGUI.current_point_index == index:
                        roiGUI.current_roi, roiGUI.current_point_index = None, None
                    else:
                        roiGUI.current_roi, roiGUI.current_point_index = roi, index
                    roiGUI.update()
                elif line_hits and roiGUI.current_point_index is None:
                    roi, index =  roiGUI.linelookup[line_hits[0][2][0]]
                    face_hit = self.hit_location(roiGUI.meshname) 
                    if face_hit:
                        x, y, z, triangle_name = face_hit
                        roiGUI.current_roi = roi
                        roiGUI.new_point(x, y, z, triangle_name, index = index)  
                        roiGUI.update()
                else:
                    face_hit = self.hit_location(roiGUI.meshname)           
                    if face_hit:
                        x, y, z, triangle_name = face_hit
                        if roiGUI.current_roi is None:
                            roiGUI.current_roi = roiGUI.new_roi()
                        if roiGUI.current_roi.being_drawn() and \
                           (roiGUI.current_roi.is_last(roiGUI.current_point_index) or roiGUI.current_roi.is_empty()):
                            roiGUI.new_point(x, y, z, triangle_name)
                        elif roiGUI.current_roi.being_drawn() and \
                             roiGUI.current_point_index == 0:
                            roiGUI.new_point(x, y, z, triangle_name, end = False)
                        elif roiGUI.current_point_index is not None:
                            roiGUI.move_point(roiGUI.current_point_index, x, y, z, triangle_name)
                    else:
                        roiGUI.current_point_index = None
                        roiGUI.current_roi = None
                    roiGUI.update()
                return True
            elif mode[0] == "Select":
                roiGUI = self.roiGUIs[mode[1]]
                face_hit = self.hit_location(roiGUI.meshname)
                if face_hit:
                    x, y, z, triangle_name = face_hit
                    triangle = self.meshes[roiGUI.meshname].faces[triangle_name]
                    roiGUI.onSelect(roiGUI, triangle)
        return False

    def OnMouseUp(self, event):

        mode = self.modePanel.GetMode()
        if mode == "Rubber Band" and self.sphere_selection is not None:
            self.placeSphere(int(self.sphere_selection))
            self.compile_band()
            self.sphere_selection = None
            return True

    def OnMouseMotion(self, event):
        if event.Dragging() and event.LeftIsDown():
            self.lastx, self.lasty = self.x, self.y
            self.x, self.y = event.GetPosition()
            mode = self.modePanel.GetMode()
            if mode == "Rotate":
                self.viewport.theta += 0.1 * (self.y - self.lasty)
                self.viewport.phi += - 0.1 * (self.x - self.lastx)
            elif mode == "Zoom":
                self.viewport.scale = self.viewport.scale * 1.01 ** (self.y - self.lasty)
                self.updateView()
            if mode == "Rubber Band" and self.sphere_selection is not None:
                self.placeSphere(int(self.sphere_selection))
                self.compile_band()
            return True

    def faceListInit(self, mesh):
        faceList = glGenLists(1)
        glNewList(faceList, GL_COMPILE)
        blocks = range(int(1 + len(mesh.faces) / BLOCKSIZE))
        for name, subvol in [(n, mesh.faces[n * BLOCKSIZE: (n+1) * BLOCKSIZE]) for n in blocks]:
            glPushName(name)
            glBegin(GL_TRIANGLES)
            for f in subvol:
                n = f.normal.normalise()
                glNormal3f(n.x, n.y, n.z)
                assert len(f.vertices) == 3
                for v in f.vertices:
                    #n = v.normal()
                    #glNormal3f(n.x, n.y, n.z)
                    glVertex(v.x, v.y, v.z)
            glEnd()
            glPopName()
        glEndList()
        self.mainNumNames = len(blocks)
        return faceList

    def vertexListInit(self, mesh):
        vertexList = glGenLists(1)
        glNewList(vertexList, GL_COMPILE)
        glMatrixMode(GL_MODELVIEW)
        for i, v in enumerate(mesh.vertices):
            glPushMatrix()
            glPushName(i)
            glTranslatef(v[0], v[1], v[2])
            glColor3f(0.2,1,0.2)
            glutSolidSphere(3, 10, 10)
            glPopName()
            glPopMatrix()
        glEndList()

        return vertexList


