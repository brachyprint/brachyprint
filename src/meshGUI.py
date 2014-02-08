#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

import wx
import sys
from wx import glcanvas
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import parseply
from mesh import makeMesh
import mesh
from math import pi, acos, sin, cos, ceil
from itertools import chain
from settings import *
from points import copy_point_cloud_excluding, makepoints, save, load, make_ply, expand
from octrees.octrees import Octree
from copy import copy

def null():
    pass

class pickPixel:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __call__(self):
        gluPickMatrix(self.x, self.y, 1, 1, glGetIntegerv(GL_VIEWPORT))

def zerocmp(x, y):
    return cmp(x[0], y[0])

class MeshCanvas(glcanvas.GLCanvas):
    def __init__(self, parent, meshes, modePanel, MeshPanel, rois):
        self.meshes = meshes
        self.modePanel = modePanel
        self.meshPanel = MeshPanel

        self.meshes_max_X = max([m.maxX for m in meshes.values()])
        self.meshes_min_X = min([m.minX for m in meshes.values()])
        self.meshes_max_Y = max([m.maxY for m in meshes.values()])
        self.meshes_min_Y = min([m.minY for m in meshes.values()])
        self.meshes_max_Z = max([m.maxZ for m in meshes.values()])
        self.meshes_min_Z = min([m.minZ for m in meshes.values()])
        self.mean_x = (self.meshes_max_X + self.meshes_min_X) / 2
        self.mean_y = (self.meshes_max_Y + self.meshes_min_Y) / 2
        self.mean_z = (self.meshes_max_Z + self.meshes_min_Z) / 2
        range_x = self.meshes_max_X - self.meshes_min_X
        range_y = self.meshes_max_Y - self.meshes_min_Y
        range_z = self.meshes_max_Z - self.meshes_min_Z
        self.range_max = (range_x ** 2 + range_y ** 2 + range_z ** 2) ** 0.5
        
        self.roiGUIs = {}
        for roiname, roi in rois.items():
            self.roiGUIs[roiname] = roiGUI(mesh = self.meshes[roi["meshname"]], **roi)
        self.band = []

        self.parent = parent

        glcanvas.GLCanvas.__init__(self, parent, -1, attribList=(glcanvas.WX_GL_DOUBLEBUFFER, ))
        self.init = False
        # initial mouse position
        self.lastx = self.x = 0
        self.lasty = self.y = 0
        self.size = None
        self.scale = 0.5
        self.theta = 0
        self.phi = 0
        self.tx, self.ty, self.tz = -self.mean_x, -self.mean_y, -self.mean_z
        #self.selection = None
        #self.sphere_selection = None
        #self.spheres = []
        #self.extra_lists = []
        
        self.mainList = {}
        self.mainNumNames = None
        self.vertexList = {}
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)

    def addMesh(self, mesh, name):
        self.meshes[name] = mesh
        self.meshes_max_X = max(self.meshes_max_X, mesh.maxX)
        self.meshes_min_X = min(self.meshes_min_X, mesh.minX)
        self.meshes_max_Y = max(self.meshes_max_Y, mesh.maxY)
        self.meshes_min_Y = min(self.meshes_min_Y, mesh.minY)
        self.meshes_max_Z = max(self.meshes_max_Z, mesh.maxZ)
        self.meshes_min_Z = min(self.meshes_min_Z, mesh.minZ)
        self.mean_x = (self.meshes_max_X + self.meshes_min_X) / 2
        self.mean_y = (self.meshes_max_Y + self.meshes_min_Y) / 2
        self.mean_z = (self.meshes_max_Z + self.meshes_min_Z) / 2
        range_x = self.meshes_max_X - self.meshes_min_X
        range_y = self.meshes_max_Y - self.meshes_min_Y
        range_z = self.meshes_max_Z - self.meshes_min_Z
        self.range_max = (range_x ** 2 + range_y ** 2 + range_z ** 2) ** 0.5

    def OnEraseBackground(self, event):
        pass # Do nothing, to avoid flashing on MSW.

    def OnSize(self, event):
        self.setSize()
        event.Skip()

    def setSize(self, selector = null):
        size = self.size = self.GetClientSize()
        if self.GetContext():
            self.SetCurrent()
            if size.width > size.height:
                yscale = self.scale
                xscale = self.scale * size.width / size.height
            else:
                xscale = self.scale
                yscale = self.scale * size.height / size.width
            glViewport(0, 0, size.width, size.height)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            selector()
            glFrustum(-xscale * self.range_max, xscale * self.range_max, -yscale * self.range_max, 
                      yscale * self.range_max, 1.0 * self.range_max, 3.0 * self.range_max)
            glTranslatef(0, 0, - 2 * self.range_max)


    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.SetCurrent()
        if not self.init:
            self.InitGL()
            self.init = True
        self.OnDraw()

    def OnMouseWheel(self, evt):
        if evt.GetWheelRotation() < 0:
            self.scale = self.scale * 1.1 # ** (self.y - self.lasty)
        else:
            self.scale = self.scale * 0.9 # ** (self.y - self.lasty)
        self.setSize()
        self.Refresh(False)

    def OnMouseDown(self, evt):
        self.CaptureMouse()
        self.x, self.y = self.lastx, self.lasty = evt.GetPosition()
        mode = self.modePanel.GetMode()
        if evt.LeftIsDown():
            if mode[0] == "Edit":
                roiGUI = self.roiGUIs[mode[1]]
                sphere_hits = self.hit(self.x, self.y, opengl_list(roiGUI.sphere_list), roiGUI.sphere_list_length())
                line_hits = self.hit(self.x, self.y, opengl_list(roiGUI.line_list), roiGUI.line_list_length())
                if sphere_hits:
                    roi, index =  roiGUI.pointlookup[sphere_hits[0][2][0]]
                    if roi == roiGUI.current_roi and \
                       roiGUI.current_roi.being_drawn() and \
                       ((roiGUI.current_point_index == 0 and roiGUI.current_roi.is_last(index)) or \
                        (roiGUI.current_roi.is_last(roiGUI.current_point_index) and index == 0)):
                        roiGUI.complete()
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
                self.Refresh(False)
            elif mode[0] == "Select":
                hits = self.hit(self.x, self.y, opengl_list(self.mainList[self.draw_mesh]), self.mainNumNames)
                if hits:
                    hits = self.hit(self.x, self.y, renderOneBlock(hits[0][2][0], self.meshes[self.draw_mesh]), BLOCKSIZE)
                    triangle = self.meshes[self.draw_mesh].faces[hits[0][2][0]]
                    edges = sum([path.get_edges() for path in self.band], [])
                    #Make list of edges to avoid.  Where there is a point in the middle of a triangle, an extra edge needs to be found.
                    #such that a full ring of avoidance edges is created.
                    avoid_edges = []
                    #Find intial vertex
                    if edges[-1].v1 in [edges[0].v1, edges[0].v2]:
                        vertex = edges[-1].v1
                    elif edges[-1].v2 in [edges[0].v1, edges[0].v2]:
                        vertex = edges[-1].v2
                    else:
                        for extra_edge in edges[-1].v1.edges:
                            if extra_edge.v1 == edges[-1].v1 and extra_edge.v2 in [edges[0].v1, edges[0].v2]:
                                    avoid_edges.append(extra_edge)
                                    vertex = extra_edge.v2
                                    break
                            if extra_edge.v2 == edges[-1].v1 and extra_edge.v1 in [edges[0].v1, edges[0].v2]:
                                    avoid_edges.append(extra_edge)
                                    vertex = extra_edge.v1
                                    break
                        for extra_edge in edges[-1].v2.edges:
                            if extra_edge.v1 == edges[-1].v2 and extra_edge.v2 in [edges[0].v1, edges[0].v2]:
                                    avoid_edges.append(extra_edge)
                                    vertex = extra_edge.v2
                                    break
                            if extra_edge.v2 == edges[-1].v2 and extra_edge.v1 in [edges[0].v1, edges[0].v2]:
                                    avoid_edges.append(extra_edge)
                                    vertex = extra_edge.v1
                                    break
                    #Go around the loop of edges, adding them to the avoidance list, and adding extra edges where necessary.
                    for edge in edges:
                        if edge.v1 == vertex:
                            vertex = edge.v2
                            avoid_edges.append(edge)
                        elif edge.v2 == vertex:
                            vertex = edge.v1
                            avoid_edges.append(edge)
                        else:
                            for extra_edge in vertex.edges:
                                if extra_edge.v1 == vertex and extra_edge.v2 == edge.v1:
                                    avoid_edges.append(extra_edge)
                                    vertex = edge.v2
                                    break
                                elif extra_edge.v1 == vertex and extra_edge.v2 == edge.v2:
                                    avoid_edges.append(extra_edge)
                                    vertex = edge.v1
                                    break
                                elif extra_edge.v2 == vertex and extra_edge.v1 == edge.v1:
                                    avoid_edges.append(extra_edge)
                                    vertex = edge.v2
                                    break
                                elif extra_edge.v2 == vertex and extra_edge.v1 == edge.v2:
                                    avoid_edges.append(extra_edge)
                                    vertex = edge.v1
                                    break
                            else:
                                assert False
                            avoid_edges.append(edge)
                    #Save the cut out mesh to a file
                    f = open(self.base_file + "rough.ply", "w")
                    roughcut = self.meshes[self.draw_mesh].cloneSubVol(triangle, avoid_edges)
                    f.write(roughcut.save_ply())
                    f.close()
                    #Expand cut out mesh and save that to a file called external
                    minx = min([v.x for v in roughcut.vertices]) - 0.01
                    maxx = max([v.x for v in roughcut.vertices]) + 0.01
                    miny = min([v.y for v in roughcut.vertices]) - 0.01
                    maxy = max([v.y for v in roughcut.vertices]) + 0.01
                    minz = min([v.z for v in roughcut.vertices]) - 0.01
                    maxz = max([v.z for v in roughcut.vertices]) + 0.01
                    points = Octree(((minx, maxx), (miny, maxy), (minz, maxz)))
                    for v in roughcut.vertices:
                        n = v.normal()
                        points.insert((v.x, v.y, v.z), (n.x, n.y, n.z))
                    external = expand(points, MOULD_THICKNESS)
                    make_ply(external, self.base_file + "external", poisson_depth = POISSON_DEPTH)
            
    def hit_location(self, meshname):
        #Find block
        hits = self.hit(self.x, self.y, opengl_list(self.mainList[meshname]), self.mainNumNames)
        if hits:
            x, y, z = gluUnProject(self.x, self.GetClientSize().height - self.y, hits[0][0])
            #Find triangle
            hits = self.hit(self.x, self.y, renderOneBlock(hits[0][2][0], self.meshes[meshname]), BLOCKSIZE)
            return x, y, z, hits[0][2][0]

    def hit(self, x, y, opengl, maxhits):
        glSelectBuffer(4 * maxhits)
        glRenderMode(GL_SELECT)
        self.setSize(pickPixel(x, self.GetClientSize().height - y)) #Set projection to single pixel
        self.setupScene()
        opengl()
        hits = glRenderMode(GL_RENDER)
        self.setSize() #Return projection to normal
        hits.sort(zerocmp)
        return hits
 
    def OnMouseUp(self, evt):
        mode = self.modePanel.GetMode()
        if mode == "Rubber Band" and self.sphere_selection is not None:
            self.placeSphere(int(self.sphere_selection))
            self.compile_band()
            self.Refresh(False)
            self.sphere_selection = None
        self.ReleaseMouse()
        self.Refresh(False)

    def OnMouseMotion(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            self.lastx, self.lasty = self.x, self.y
            self.x, self.y = evt.GetPosition()
            mode = self.modePanel.GetMode()
            if mode == "Rotate":
                self.theta += 0.1 * (self.y - self.lasty)
                self.phi += - 0.1 * (self.x - self.lastx)
            elif mode == "Zoom":
                self.scale = self.scale * 1.01 ** (self.y - self.lasty)
                self.setSize()
            if mode == "Rubber Band" and self.sphere_selection is not None:
                self.placeSphere(int(self.sphere_selection))
                self.compile_band()
            self.Refresh(False)


    def InitGL(self):
        # set viewing projection
        self.setSize()

        glutInit()
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)

        glInitNames()
        for key, mesh in self.meshes.items():
            self.mainList[key] = glGenLists (1)
            self.mainListInitial(self.mainList[key], mesh)
            self.vertexListInit(key, mesh)
        for roiname, roigui in self.roiGUIs.items():
            roigui.InitGL()

    def mainListInitial(self, name, mesh):
        glNewList(name, GL_COMPILE)
        blocks = range(1 + len(mesh.faces) / BLOCKSIZE)
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

    def vertexListInit(self, key, mesh):
        self.vertexList[key] = glGenLists(1)
        glNewList(self.vertexList[key], GL_COMPILE)
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

    def OnDraw(self):
        # clear color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.setupScene()
        for name in self.meshes.keys():
            style = self.meshPanel.getStyle(name)
            if style == "Red":
                glColor3f(1.0,0.7, 0.7)
            elif style == "Blue":
                glColor3f(0.7,0.7, 1.0)
            else:
                glColor3f(1.0, 1.0, 1.0)
            if self.meshPanel.getVisible(name):
                glCallList(self.mainList[name])
        glMatrixMode(GL_MODELVIEW)
        for name in self.meshes.keys():
            if self.meshPanel.getShowVertices(name): 
                glCallList(self.vertexList[name])
        for roiGUI in self.roiGUIs.values():
            glCallList(roiGUI.sphere_list)
            glCallList(roiGUI.line_list)


        if self.parent.showgrid.GetValue():
            self.drawXAxisGrid()
            self.drawYAxisGrid()
            self.drawZAxisGrid()

        self.SwapBuffers()

    def setupScene(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glRotatef(self.theta, 1.0, 0.0, 0.0)
        glRotatef(self.phi, 0.0, 1.0, 0.0)
        glTranslatef(self.tx, self.ty, self.tz)

    def drawXAxisGrid(self):
        rangex = []
        rangey = [self.meshes_min_Y, self.meshes_max_Y]
        rangez = [self.meshes_min_Z, self.meshes_max_Z]
        self.drawGrid(rangex, rangey, rangez)

    def drawYAxisGrid(self):
        rangex = [self.meshes_min_X, self.meshes_max_X]
        rangey = []
        rangez = [self.meshes_min_Z, self.meshes_max_Z]
        self.drawGrid(rangex, rangey, rangez)

    def drawZAxisGrid(self):
        rangex = [self.meshes_min_X, self.meshes_max_X]
        rangey = [self.meshes_min_Y, self.meshes_max_Y]
        rangez = []
        self.drawGrid(rangex, rangey, rangez)

    def drawGrid(self, rangex, rangey, rangez, numLines=10):
        '''
            drawGrid -- draw a grid of lines on an axis

            Arguments:
                rangex -- min and max X coordinates
                rangey -- min and max Y coordinates
                rangez -- min and max Z coordinates
                numLines -- the number of lines on the smallest axis
        '''
        d = [float('inf')]*3
        if rangex:
            d[0] = (rangex[1]-rangex[0])/numLines
        if rangey:
            d[1] = (rangey[1]-rangey[0])/numLines
        if rangez:
            d[2] = (rangez[1]-rangez[0])/numLines

        d = min(d)

        xs = []; ys = []; zs = []
        if rangex:
            numx = int(ceil(-rangex[0]/d)) + int(ceil(rangex[1])/d)
            offx = int(ceil(rangex[0]/d))
            xs = map(lambda x: x*d + offx*d, range(numx))
        else:
            rangex = [0,0]

        if rangey:
            numy = int(ceil(-rangey[0]/d)) + int(ceil(rangey[1])/d)
            offy = int(ceil(rangey[0]/d))
            ys = map(lambda y: y*d + offy*d, range(numy))
        else:
            rangey = [0,0]

        if rangez:
            numz = int(ceil(-rangez[0]/d)) + int(ceil(rangez[1])/d)
            offz = int(ceil(rangez[0]/d))
            zs = map(lambda z: z*d + offz*d, range(numz))
        else:
            rangez = [0,0]

        halfGridSize = 100; inc = 10
        glBegin(GL_LINES);
        glColor3f(0.75, 0.75, 0.75);

        for x in xs:
            glVertex3f(x,rangey[0],rangez[0])
            glVertex3f(x,rangey[-1],rangez[-1])

        for y in ys:
            glVertex3f(rangex[0],y,rangez[0])
            glVertex3f(rangex[-1],y,rangez[-1])

        for z in zs:
            glVertex3f(rangex[0],rangey[0],z)
            glVertex3f(rangex[-1],rangey[-1],z)

        glEnd()
     
class ROI:
    def __init__(self):
        self.paths = []
        self.points = []
    def new_point(self, x, y, z, face_name, end, index):
        if index is not None:
            print self.points
            self.points = self.points[:index + 1] + [(x, y, z, face_name)] + self.points[index+1:]
            temp = copy(self.paths)
            self.paths = temp[:index] + [None, None] + temp[index+1:]
            print self.points
            return index + 1
        elif end:
            self.points.append((x, y, z, face_name))
            if len(self.points) > 1:
                self.paths.append(None)
            return len(self.points) - 1
        else:
            self.points = [(x, y, z, face_name)] + self.points
            if len(self.points) > 1:
                self.paths = [None] + self.paths
            return 0
    def being_drawn(self):
        return len(self.points) == 0 or len(self.paths) < len(self.points)
    def is_empty(self):
        return len(self.points) == 0
    def is_last(self, i):
        return i == len(self.points) - 1

class roiGUI:
    def __init__(self, mesh, meshname, closed, onSelect=None):
        self.meshname = meshname
        self.mesh = mesh
        self.closed = closed
        self.onSelect = onSelect
        self.rois = []
        self.current_roi = None
        self.current_point_index = None
        self.pointlookup = []
        self.linelookup = []
    def InitGL(self):
        self.line_list = glGenLists(1)
        self.sphere_list = glGenLists(1)
        self.compile_sphere_list()
        self.compile_line_list()
    def new_roi(self):
        r = ROI()
        self.rois.append(r)
        return r
    def new_point(self, x, y, z, face_name, end = True, index=None):
        print "Start", index
        if self.current_roi:
            self.current_point_index = self.current_roi.new_point(x, y, z, face_name, end, index)
    def move_point(self, i, x, y, z, face_name):
        if self.current_roi:
            self.current_roi.points[i] = (x, y, z, face_name)
            if i > 0:
                self.current_roi.paths[i - 1] = None
            else:
                if not self.current_roi.being_drawn():
                    self.current_roi.paths[-1] = None
            if i < len(self.current_roi.paths):
                self.current_roi.paths[i] = None
            else:
                if not self.current_roi.being_drawn():
                    self.current_roi.paths[0] = None
            
    def complete(self):
        assert self.current_roi.being_drawn() == True
        if self.closed == True:
            self.current_roi.paths.append(None)
    def compile_sphere_list(self):
        name = 0
        self.pointlookup = []
        glNewList(self.sphere_list, GL_COMPILE)
        glMatrixMode(GL_MODELVIEW)
        for roi in self.rois:
            for i, sphere in enumerate(roi.points):
                glPushMatrix()
                glPushName(name)
                self.pointlookup.append((roi, i))
                name = name + 1
                glTranslatef(sphere[0], sphere[1], sphere[2])
                glColor3f(0.2,1,0.2)
                glutSolidSphere(7, 10, 10)
                glPopName()
                glPopMatrix()
        if self.current_point_index is not None:
            sphere = self.current_roi.points[self.current_point_index]
            glPushMatrix()
            glTranslatef(sphere[0], sphere[1], sphere[2])
            glColor3f(1,0.2,0.2)
            glutSolidSphere(10, 11, 11)
            glPopMatrix()
        glEndList()    
    def compile_line_list(self):
        name = 0
        self.linelookup = []
        glNewList(self.line_list, GL_COMPILE)
        glColor3f(0.2,1,0.2)
        for roi in self.rois:
            for index, path_list in enumerate(roi.paths):
                glPushName(name)
                for path in path_list:
                    self.linelookup.append((roi, index))
                    name = name + 1
                    for start, end in path.points():
                        dx = start[0] - end[0]
                        dy = start[1] - end[1]
                        dz = start[2] - end[2]
                        length_d = (dx ** 2 + dy ** 2 + dz ** 2) ** 0.5
                        if length_d > 0:
                            #axis of rotation = (0, 0, 1) cross (dx, dy, dz) = (-dy, dx, 0)
                            #angle to rotate = 180.0 / pi * acos((0,0,1).(dx, dy, dz) / (dx, dy, dz).(dx, dy, dz))
                            glPushMatrix()
                            glTranslatef(start[0], start[1], start[2])
                            glRotatef(180.0 / pi * acos(dz / length_d), -dy, dx, 0)
                            glutSolidSphere(3, 10, 10)
                            glutSolidCylinder(3, -length_d, 20 ,20)
                            glPopMatrix()
                glPopName() 
        glEndList()
    def update(self):
        for roi in self.rois:
            for index, path in enumerate(roi.paths):
                if path is None:
                    if index + 1 < len(roi.points):
                        roi.paths[index] = self.mesh.get_path(roi.points[index], roi.points[index + 1])
                    else:
                        roi.paths[index] = self.mesh.get_path(roi.points[index], roi.points[0])
        self.compile_sphere_list()
        self.compile_line_list()
    def sphere_list_length(self):
        return len(self.pointlookup)
    def line_list_length(self):
        return len(self.linelookup)

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

class ModePanel(wx.Panel):
           
    def __init__(self, parent, rois, *args, **kw):
        super(ModePanel, self).__init__(parent, *args, **kw) 
        self.rois = rois
        self.InitUI()
        
    def InitUI(self):
        box = wx.BoxSizer(wx.VERTICAL)   
        self.rb_rotate = wx.RadioButton(self, label='Rotate',  style=wx.RB_GROUP)
        self.rb_zoom = wx.RadioButton(self, label='Zoom')
        self.rb_edits = {}
        self.rb_selects = {}
        box.Add(self.rb_rotate, 0.5, wx.EXPAND)
        box.Add(self.rb_zoom, 0.5, wx.EXPAND)
        for roiname, roi in self.rois.items():
            self.rb_edits[roiname] = wx.RadioButton(self, label='Edit %s' % roiname)
            box.Add(self.rb_edits[roiname], 0.5, wx.EXPAND)
            if roi.has_key("onSelect"):
                self.rb_selects[roiname] = wx.RadioButton(self, label='Select %s' % roiname)
                box.Add(self.rb_selects[roiname], 0.5, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()

    def GetMode(self):
        if self.rb_rotate.GetValue():  return "Rotate"
        if self.rb_zoom.GetValue(): return "Zoom"  
        for roiname, rb in self.rb_edits.items(): 
            if rb.GetValue(): return "Edit", roiname  
        for roiname, rb in self.rb_selects.items(): 
            if rb.GetValue(): return "Select", roiname

class MeshPanel(wx.Panel):
    '''
        MeshPanel -- display a panel of information about the loaded meshes
    '''
    def __init__(self, parent, meshnames, *args, **kw):
        self.parent = parent
        self.meshnames = meshnames
        self.cbs = {}
        self.visible = {}
        self.vertices = {}
        super(MeshPanel, self).__init__(parent, *args, **kw) 
        self.InitUI()
        
    def InitUI(self):   
        self.box = wx.GridBagSizer(3, 10)

        titles = ["Name", "Show?", "Vertices?", "Colour"]
        for i in range(4):
            self.box.Add(wx.StaticText(self, -1, titles[i]), wx.GBPosition(0, i))

        self.box.Add(wx.StaticLine(self, -1), wx.GBPosition(1, 0), span=wx.GBSpan(1, 4), flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=3)

        self.cols = 2

        for meshname in self.meshnames:
            self.addMesh(meshname)
            
        self.SetAutoLayout(True)
        self.SetSizer(self.box)
        self.Layout()
        self.Bind(wx.EVT_COMBOBOX, self.OnChange)
        self.Bind(wx.EVT_CHECKBOX, self.OnChange)

    def addMesh(self, meshname):
        styles = ["Red", "Blue"]

        self.cbs[meshname] = wx.ComboBox(self, -1, choices=styles, style=wx.CB_READONLY)
        width, height = self.cbs[meshname].GetSize()
        dc = wx.ClientDC (self.cbs[meshname])
        tsize = max ( (dc.GetTextExtent (c)[0] for c in styles) )
        self.cbs[meshname].SetMinSize((tsize+50, height))
        self.cbs[meshname].SetStringSelection(styles[0])
        self.visible[meshname] = wx.CheckBox(self, -1, "")
        self.visible[meshname].SetValue(True)
        self.vertices[meshname] = wx.CheckBox(self, -1, "")
        self.vertices[meshname].SetValue(False)
        self.box.Add(wx.StaticText(self, -1, meshname), wx.GBPosition(self.cols, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        self.box.Add(self.visible[meshname], wx.GBPosition(self.cols, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        self.box.Add(self.vertices[meshname], wx.GBPosition(self.cols, 2), flag=wx.ALIGN_CENTER_VERTICAL)
        self.box.Add(self.cbs[meshname], wx.GBPosition(self.cols, 3), flag=wx.ALIGN_CENTER_VERTICAL)
        self.cols += 1

    def getStyle(self, meshname):
        return self.cbs[meshname].GetValue()
            
    def getVisible(self, meshname):
        return self.visible[meshname].GetValue()

    def getShowVertices(self, meshname):
        return self.vertices[meshname].GetValue()

    def OnChange(self, event):
        self.parent.Refresh()

class MainWindow(wx.Frame):
    def __init__(self, parent = None, id = -1, title = "Brachyprint mould viewer", rois = [], meshes={}):
        # Init
        wx.Frame.__init__(
                self, parent, id, title, size = (400,300),
                style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE
        )

        # TextCtrl
        # self.control = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE)
        
        #self.control = ConeCanvas(self)
        self.modePanel = ModePanel(self, rois)
        self.meshPanel = MeshPanel(self, meshes.keys(), style=wx.SUNKEN_BORDER)
        
        vbox = wx.BoxSizer(wx.VERTICAL) 
        box = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(self.meshPanel, 0.5, wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.modePanel, 0.5, wx.EXPAND)

        self.showgrid = wx.CheckBox(self, label="Show grid")
        vbox.Add(self.showgrid, 0, wx.TOP, 20)

        box.Add(vbox, 0.5, wx.EXPAND)

        # create the meshes
        self.meshes = meshes            
        self.meshCanvas = MeshCanvas(self, self.meshes, self.modePanel, self.meshPanel, rois)
        box.Add(self.meshCanvas, 1, wx.EXPAND)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()

        self.showgrid.Bind(wx.EVT_CHECKBOX, lambda x: self.meshCanvas.OnDraw())

        # StatusBar
        #self.CreateStatusBar()

        # Filemenu
        filemenu = wx.Menu()

        # Filemenu - About
        menuitem = filemenu.Append(-1, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, menuitem) # here comes the event-handler
        # Filemenu - Separator
        filemenu.AppendSeparator()

        # Filemenu - Exit
        menuitem = filemenu.Append(-1, "E&xit", "Terminate the program")
        self.Bind(wx.EVT_MENU, self.OnExit, menuitem) # here comes the event-handler

        # Menubar
        menubar = wx.MenuBar()
        menubar.Append(filemenu,"&File")
        self.SetMenuBar(menubar)

        # Show
        self.Show(True)

        # Maximise the window
        self.Maximize()

    def Refresh(self):
        self.meshCanvas.Refresh(False)

    def OnAbout(self,event):
        message = "Viewer for brachyprint moulds"
        caption = "Brachyprint mould viewer"
        wx.MessageBox(message, caption, wx.OK)

    def OnExit(self,event):
        self.Close(True)  # Close the frame.

