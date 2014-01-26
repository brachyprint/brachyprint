#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

import wx
import sys
from wx import glcanvas
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import parseply, model
from math import pi, acos
from heapq import heappush, heappop
from itertools import chain
from settings import *
from points import copy_point_cloud_excluding, makepoints, save, load, make_ply, expand
from octrees.octrees import Octree

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
    def __init__(self, parent, meshes, modePanel, MeshPanel, base_file, draw_mesh):
        self.meshes = meshes
        self.modePanel = modePanel
        self.meshPanel = MeshPanel
        self.base_file = base_file
        self.draw_mesh = draw_mesh
        meshes_max_X = max([m.maxX for m in meshes.values()])
        meshes_min_X = max([m.minX for m in meshes.values()])
        meshes_max_Y = max([m.maxY for m in meshes.values()])
        meshes_min_Y = max([m.minY for m in meshes.values()])
        meshes_max_Z = max([m.maxZ for m in meshes.values()])
        meshes_min_Z = max([m.minZ for m in meshes.values()])
        self.mean_x = (meshes_max_X + meshes_min_X) / 2
        self.mean_y = (meshes_max_Y + meshes_min_Y) / 2
        self.mean_z = (meshes_max_Z + meshes_min_Z) / 2
        range_x = meshes_max_X - meshes_min_X
        range_y = meshes_max_Y - meshes_min_Y
        range_z = meshes_max_Z - meshes_min_Z
        self.range_max = (range_x ** 2 + range_y ** 2 + range_z ** 2) ** 0.5
        self.band = []

        glcanvas.GLCanvas.__init__(self, parent, -1, attribList=(glcanvas.WX_GL_DOUBLEBUFFER, ))
        self.init = False
        # initial mouse position
        self.lastx = self.x = 0
        self.lasty = self.y = 0
        self.size = None
        self.scale = 0.5
        self.theta = 0
        self.phi = 0
        self.selection = None
        self.sphere_selection = None
        self.spheres = []
        self.extra_lists = []
        self.mainList = {}
        self.mainNumNames = None
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)

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

    def OnMouseDown(self, evt):
        self.CaptureMouse()
        self.x, self.y = self.lastx, self.lasty = evt.GetPosition()
        mode = self.modePanel.GetMode()
        if mode == "Rubber Band":
            hits = self.hit(self.x, self.y, opengl_lists(self.extra_lists), len(self.spheres))
            if hits:
                self.sphere_selection =  hits[0][2][0]
            else:
                self.sphere_selection = None           
                self.placeSphere()
            self.compile_band()
            self.Refresh(False)
        elif mode == "Select Cut":
            hits = self.hit(self.x, self.y, opengl_list(self.mainList[self.draw_mesh]), self.mainNumNames)
            if hits:
                hits = self.hit(self.x, self.y, renderOneBlock(hits[0][2][0], self.meshes[self.draw_mesh]), BLOCKSIZE)
                triangle = self.meshes[self.draw_mesh].faces[hits[0][2][0]]
                edges = sum([path.get_edges() for path in self.band], [])
                avoid_edges = []
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
                f = open(self.base_file + "rough.ply", "w")
                roughcut = self.meshes[self.draw_mesh].cloneSubVol(triangle, avoid_edges)
                f.write(roughcut.save_ply())
                f.close()
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

    def update_band(self):
        self.band = []
        if len(self.spheres) > 0:
            for i, (sphere, nextsphere) in enumerate(zip(self.spheres, self.spheres[1:] + [self.spheres[0]])):
                self.band = self.band + self.get_path(sphere, nextsphere)
                


    def compile_band(self):
        self.update_band()
        glNewList(self.extra_lists[0], GL_COMPILE)
        if len(self.spheres) > 0:
            for i, (sphere, nextsphere) in enumerate(zip(self.spheres, self.spheres[1:] + [self.spheres[0]])):
                glPushMatrix()
                glPushName(i)
                glTranslatef(sphere[0], sphere[1], sphere[2])
                glColor3f(0.2,1,0.2)
                glutSolidSphere(7, 10, 10)
                glPopName()
                glPopMatrix()
        for path in self.band:
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
        glEndList()
            
    def placeSphere(self, i = None):
        #Find block
        hits = self.hit(self.x, self.y, opengl_list(self.mainList[self.draw_mesh]), self.mainNumNames)
        if hits:
            x, y, z = gluUnProject(self.x, self.GetClientSize().height - self.y, hits[0][0])
            #Find triangle
            hits = self.hit(self.x, self.y, renderOneBlock(hits[0][2][0], self.meshes[self.draw_mesh]), BLOCKSIZE)
            if i is None:
                self.spheres.append((x, y, z, hits[0][2][0]))
            else:
                self.spheres[i] = (x, y, z, hits[0][2][0])

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
        self.extra_lists = [glGenLists (1)]

    def mainListInitial(self, name, mesh):
        glNewList(name, GL_COMPILE)
        blocks = range(1 + len(mesh.faces) / BLOCKSIZE)
        for name, subvol in [(n, mesh.faces[n * BLOCKSIZE: (n+1) * BLOCKSIZE]) for n in blocks]:
            glPushName(name)
            glBegin(GL_TRIANGLES)
            for f in subvol:
                assert len(f.vertices) == 3
                for v in f.vertices:
                    n = v.normal()
                    glNormal3f(n.x, n.y, n.z)
                    glVertex(v.x, v.y, v.z)
            glEnd()
            glPopName()
        glEndList()   
        self.mainNumNames = len(blocks) 

    def OnDraw(self):
        # clear color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.setupScene()
        for name in self.meshes.keys():
            style = self.meshPanel.getStyle(name)
            print style
            if style == "Red":
                glColor3f(1.0,0.7, 0.7)
            elif style == "Blue":
                glColor3f(0.7,0.7, 1.0)
            else:
                glColor3f(1.0, 1.0, 1.0)
            if style != "Hidden":
                glCallList(self.mainList[name])
        glMatrixMode(GL_MODELVIEW)
        for list_ in self.extra_lists:
            glCallList(list_)
        self.SwapBuffers()

    def setupScene(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glRotatef(self.theta, 1.0, 0.0, 0.0)
        glRotatef(self.phi, 0.0, 1.0, 0.0)
        glTranslatef(-self.mean_x, -self.mean_y, -self.mean_z)

    def get_path(self, s1, s2):
        s2Postion = s2[0], s2[1], s2[2]
        s2Face = self.meshes[self.draw_mesh].faces[s2[3]]
        priority_queue = []
        visited = {}
        if s1[3] == s2[3]:
            return [point_to_point(s1, s2)]
        for v in self.meshes[self.draw_mesh].faces[s1[3]].vertices:
            pv = point_to_vertex(s1[0], s1[1], s1[2], v, s2Postion, s2Face)
            heappush(priority_queue, (pv.dist() + pv.crowdist(), pv.dist(), [pv]))	
        while (len(priority_queue) > 0):
            dist_plus_crow, dist, paths = heappop(priority_queue)
            lastPath = paths[-1]
            end = lastPath.end()
            if end not in visited:
                if lastPath.finished():
                    #Finished!
                    return paths
                else:
                    visited[end] = True
                    for newPath in lastPath.new_Paths():
                        new_dist = newPath.dist()
                        heappush(priority_queue, (dist + new_dist + pv.crowdist(), dist + new_dist, paths + [newPath]))

class point_to_point:
    def __init__(self, s, e, endPoint = None, endFace = None):
        self.s, self.e = s,e 
    def points(self):
        return [((self.s[0], self.s[1], self.s[2]), (self.e[0], self.e[1], self.e[2]))]
    def get_edges(self):
        return []

class point_to_vertex:
    def __init__(self, sx, sy, sz, e, endPoint = None, endFace = None):
        self.sx, self.sy, self.sz, self.e = sx, sy, sz, e
        self.endPoint, self.endFace = endPoint, endFace
    def dist(self):
        return ((self.sx - self.e.x) ** 2 + (self.sy - self.e.y) ** 2 + (self.sz - self.e.z) ** 2) ** 0.5
    def crowdist(self):
        return ((self.e.x - self.endPoint[0]) ** 2 + (self.e.y - self.endPoint[1]) ** 2 + (self.e.z - self.endPoint[2]) ** 2) ** 0.5
    def end(self):
        return self.e
    def points(self):
        return [((self.sx, self.sy, self.sz), (self.e.x, self.e.y, self.e.z))]
    def new_Paths(self):
        results = [follow_edge(self.e, v, self.endPoint, self.endFace, edge) for v, edge in self.e.adjacent_verticies()] 
        if self.endPoint is not None and self.endFace in self.e.faces:
            results += [vertex_to_point(self.e, self.endPoint)]
        return results
    def finished(self):
        return False
    def get_edges(self):
        return []
    #def __str__(self):
     

class follow_edge:
    def __init__(self, s, e, endPoint = None, endFace = None, edge = None):
        self.s, self.e = s, e
        self.endPoint, self.endFace = endPoint, endFace
        self.edge = edge
    def dist(self):
        return ((self.s.x - self.e.x) ** 2 + (self.s.y - self.e.y) ** 2 + (self.s.z - self.e.z) ** 2) ** 0.5
    def end(self):
        return self.e
    def points(self):
        return [((self.s.x, self.s.y, self.s.z), (self.e.x, self.e.y, self.e.z))]
    def new_Paths(self):
        results =  [follow_edge(self.e, v, self.endPoint, self.endFace, edge) for v, edge in self.e.adjacent_verticies()] 
        if self.endPoint is not None and self.endFace in self.e.faces:
            results += [vertex_to_point(self.e, self.endPoint)]
        return results
    def finished(self):
        return False
    def crowdist(self):
        return ((self.e.x - self.endPoint[0]) ** 2 + (self.e.y - self.endPoint[1]) ** 2 + (self.e.z - self.endPoint[2]) ** 2) ** 0.5
    def get_edges(self):
        return [self.edge]

class vertex_to_point:
    def __init__(self, s, (ex, ey, ez)):
        self.s, self.ex, self.ey, self.ez = s, ex, ey, ez
    def dist(self):
        return ((self.s.x - self.ex) ** 2 + (self.s.y - self.ey) ** 2 + (self.s.z - self.ez) ** 2) ** 0.5
    def finished(self):
        return True
    def points(self):
        return [((self.s.x, self.s.y, self.s.z), (self.ex, self.ey, self.ez))]
    def end(self):
        return "Finished!!!"
    def get_edges(self):
        return []

class opengl_lists:
    def __init__(self, lists):
        self.lists = lists
    def __call__(self):
        for l in self.lists:
            glCallList(l)

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
           
    def __init__(self, *args, **kw):
        super(ModePanel, self).__init__(*args, **kw) 
        
        self.InitUI()
        
    def InitUI(self):   
        self.rb_rotate = wx.RadioButton(self, label='Rotate',  style=wx.RB_GROUP)
        self.rb_zoom = wx.RadioButton(self, label='Zoom')
        #self.rb_select = wx.RadioButton(self, label='Select')
        self.rb_band = wx.RadioButton(self, label='Rubber Band')
        self.rb_inside = wx.RadioButton(self, label='Select Cut')

        #self.rb_rotate.Bind(wx.EVT_RADIOBUTTON, self.SetMode)
        #self.rb_zoom.Bind(wx.EVT_RADIOBUTTON, self.SetMode)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.rb_rotate, 0.5, wx.EXPAND)
        box.Add(self.rb_zoom, 0.5, wx.EXPAND)
        #box.Add(self.rb_select, 0.5, wx.EXPAND)
        box.Add(self.rb_band, 0.5, wx.EXPAND)
        box.Add(self.rb_inside, 0.5, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()

    def GetMode(self):
        if self.rb_rotate.GetValue():  return "Rotate"
        if self.rb_zoom.GetValue(): return "Zoom"  
        #if self.rb_select.GetValue(): return "Select"  
        if self.rb_band.GetValue(): return "Rubber Band"  
        if self.rb_inside.GetValue(): return "Select Cut"

class MeshPanel(wx.Panel):
           
    def __init__(self, parent, meshnames, *args, **kw):
        self.parent = parent
        self.meshnames = meshnames
        self.cbs = {}
        super(MeshPanel, self).__init__(parent, *args, **kw) 
        self.InitUI()
        
    def InitUI(self):   
        box = wx.BoxSizer(wx.VERTICAL)
        styles = ["Hidden", "Red", "Blue"]
        for meshname in self.meshnames:
            box.Add(wx.StaticText(self, -1, meshname))
            self.cbs[meshname] = wx.ComboBox(self, -1, choices=styles, style=wx.CB_READONLY)
            box.Add(self.cbs[meshname], 0.5, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()
        self.Bind(wx.EVT_COMBOBOX, self.OnChange)

    def getStyle(self, meshname):
        return self.cbs[meshname].GetValue()

    def OnChange(self, event):
        self.parent.Refresh()

class MainWindow(wx.Frame):
    def __init__(self, ply_files, parent = None, id = -1, title = "PyOpenGL Example 1", base_filename = "", draw_mesh = ""):
        # Init
        wx.Frame.__init__(
                self, parent, id, title, size = (400,300),
                style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE
        )

        # TextCtrl
        # self.control = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE)
        
        #self.control = ConeCanvas(self)
        self.modePanel = ModePanel(self)
        self.meshPanel = MeshPanel(self, ply_files.keys())
        
        vbox = wx.BoxSizer(wx.VERTICAL) 
        box = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(self.meshPanel, 0.5, wx.EXPAND)
        vbox.Add(self.modePanel, 0.5, wx.EXPAND)
        box.Add(vbox, 0.5, wx.EXPAND)
        self.base_file = base_filename
        self.meshes = {}
        for name, filename in ply_files.items():
            f = open(filename)
            self.meshes[name] = model.makeMesh(parseply.parseply(f))
            f.close()
            
        self.meshCanvas = MeshCanvas(self, self.meshes, self.modePanel, self.meshPanel, self.base_file, draw_mesh)
        box.Add(self.meshCanvas, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()


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

    def Refresh(self):
        self.meshCanvas.Refresh(False)

    def OnAbout(self,event):
        message = "Using PyOpenGL in wxPython"
        caption = "About PyOpenGL Example"
        wx.MessageBox(message, caption, wx.OK)

    def OnExit(self,event):
        self.Close(True)  # Close the frame.

