
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
A wxPython widget for displaying OpenGL objects.

Use in conjuction with the MeshController class for an MVC mesh viewer.
'''

from __future__ import division

import wx
from wx import glcanvas
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class pickPixel:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __call__(self):
        gluPickMatrix(self.x, self.y, 1, 1, glGetIntegerv(GL_VIEWPORT))


class MeshCanvas(glcanvas.GLCanvas):
    def __init__(self, parent):
        self.parent = parent
        self.controller = None

        glcanvas.GLCanvas.__init__(self, parent, -1, attribList=(glcanvas.WX_GL_DOUBLEBUFFER, ))
        self.init = False

        #self.triangleList = {}
        #self.vertexList = {}

        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self.Bind(wx.EVT_CHAR, self.OnKeyPress)

        # hog the key focus
        self.Bind(wx.EVT_KILL_FOCUS, lambda evt: self.SetFocus())
        self.SetFocus()

    def setController(self, controller):
        '''Set the controller class for the view (MVC pattern).
        '''
        self.controller = controller

    #def updateViewPort(self, viewport):
    #    self.viewport = viewport

    def OnKeyPress(self, event):
        '''Propagate KeyPress events to the controller.
        '''
        if self.controller:
            if self.controller.OnKeyPress(event):
                self.Refresh(False)

    def OnEraseBackground(self, event):
        pass # Do nothing, to avoid flashing on MSW.

    def OnSize(self, event):
        '''Propagate Size events to the controller.
        '''
        if self.controller:
            if self.controller.OnSize(event):
                self.Refresh(False)

        # propagate the event
        event.Skip()

    def OnPaint(self, event):
        '''Repaint the widget.
        '''
        dc = wx.PaintDC(self)
        self.SetCurrent()
        if not self.init:
            self.InitGL()
            self.init = True
        self.OnDraw()

    def OnMouseWheel(self, event):
        '''Propagate MouseWheel events to the controller.
        '''
        # send event to controller
        if self.controller:
            if self.controller.OnMouseWheel(event):
                self.Refresh(False)

    def OnMouseDown(self, event):
        '''Propagate MouseDown events to the controller.
        '''
        self.CaptureMouse()

        # send event to controller
        if self.controller:
            if self.controller.OnMouseDown(event):
                self.Refresh(False)
 
    def OnMouseUp(self, event):
        '''Propagate MouseUpSize events to the controller.
        '''
        # send event to controller
        if self.controller:
            if self.controller.OnMouseUp(event):
                self.Refresh(False)

        self.ReleaseMouse()

    def OnMouseMotion(self, event):
        '''Propagate MouseMotion events to the controller.
        '''
        # send event to controller
        if self.controller:
            if self.controller.OnMouseMotion(event):
                self.Refresh(False)

    def InitGL(self):

        glutInit()
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)

        glInitNames()

        # TODO:
        if self.controller:
            self.controller.InitGL()

    def OnDraw(self):
        '''Redraw the widget.
        '''
        # clear color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.setupScene()
        for k in self.displayObjects.keys():
            obj = self.displayObjects[k]
            glMatrixMode(obj["matrix_mode"])
            style = obj["style"]
            if style == "Red":
                glColor3f(1.0, 0.7, 0.7)
            elif style == "Blue":
                glColor3f(0.7, 0.7, 1.0)
            else:
                glColor3f(1.0, 1.0, 1.0)
            visible = obj["visible"]
            
            if visible:
                glCallList(obj["list"])
        if False:
            glMatrixMode(GL_MODELVIEW)
            for name in self.meshes.keys():
                if self.meshPanel.getShowVertices(name): 
                    glCallList(self.vertexList[name])
            for roiGUI in self.roiGUIs.values():
                glCallList(roiGUI.sphere_list)
                glCallList(roiGUI.line_list)

        #if self.parent.showgrid.GetValue():
        #    self.drawXAxisGrid()
        #    self.drawYAxisGrid()
        #    self.drawZAxisGrid()

        self.SwapBuffers()

    def updateViewPort(self, selector = lambda: None):
        if self.GetContext():
            self.SetCurrent()
            glViewport(0, 0, self.viewport.width, self.viewport.height)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            selector()

            xscale = self.viewport.xscale()
            yscale = self.viewport.yscale()
            range_max = self.viewport.range_max
            glFrustum(-xscale * range_max, xscale * range_max, -yscale * range_max, 
                      yscale * range_max, 1.0 * range_max, 3.0 * range_max)
            glTranslatef(0, 0, - 2 * range_max)

    def setupScene(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glRotatef(self.viewport.theta, 1.0, 0.0, 0.0)
        glRotatef(self.viewport.phi, 0.0, 1.0, 0.0)
        glTranslatef(self.viewport.tx, self.viewport.ty, self.viewport.tz)

    def hit(self, x, y, opengl, maxhits):
        glSelectBuffer(4 * maxhits)
        glRenderMode(GL_SELECT)
        self.updateViewPort(pickPixel(x, self.GetClientSize().height - y)) #Set projection to single pixel
        self.setupScene()
        opengl()
        hits = glRenderMode(GL_RENDER)
        self.updateViewPort() #Return projection to normal
        #hits.sort(zerocmp)
        hits.sort(lambda x,y: cmp(x[0], y[0]))
        return hits

    def drawXAxisGrid(self, d=10):
        rangex = []
        rangey = [self.meshes.min_Y, self.meshes.max_Y]
        rangez = [self.meshes.min_Z, self.meshes.max_Z]
        self.drawGrid(rangex, rangey, rangez, d)

    def drawYAxisGrid(self, d=10):
        rangex = [self.meshes.min_X, self.meshes.max_X]
        rangey = []
        rangez = [self.meshes.min_Z, self.meshes.max_Z]
        self.drawGrid(rangex, rangey, rangez, d)

    def drawZAxisGrid(self, d=10):
        rangex = [self.meshes.min_X, self.meshes.max_X]
        rangey = [self.meshes.min_Y, self.meshes.max_Y]
        rangez = []
        self.drawGrid(rangex, rangey, rangez, d)

    def calcGridSize(self, numLines=10):
        rangex = [self.meshes.min_X, self.meshes.max_X]
        rangey = [self.meshes.min_Y, self.meshes.max_Y]
        rangez = [self.meshes.min_Z, self.meshes.max_Z]

        d = [float('inf')]*3
        if rangex:
            d[0] = (rangex[1]-rangex[0])/numLines
        if rangey:
            d[1] = (rangey[1]-rangey[0])/numLines
        if rangez:
            d[2] = (rangez[1]-rangez[0])/numLines

        d = min(d)
        return d

    def drawGrid(self, rangex, rangey, rangez, d):
        '''
            drawGrid -- draw a grid of lines on an axis

            Arguments:
                rangex -- min and max X coordinates
                rangey -- min and max Y coordinates
                rangez -- min and max Z coordinates
                numLines -- the number of lines on the smallest axis
        '''

        xs = []; ys = []; zs = []
        if rangex:
            numx = int(floor(-rangex[0]/d)) + int(ceil(rangex[1])/d) + 1
            offx = int(ceil(rangex[0]/d))
            xs = map(lambda x: x*d + offx*d, range(numx))
        else:
            rangex = [0,0]

        if rangey:
            numy = int(floor(-rangey[0]/d)) + int(ceil(rangey[1])/d) + 1
            offy = int(ceil(rangey[0]/d))
            ys = map(lambda y: y*d + offy*d, range(numy))
        else:
            rangey = [0,0]

        if rangez:
            numz = int(floor(-rangez[0]/d)) + int(ceil(rangez[1])/d) + 1
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


    def Screenshot(self, filename="screenshot.jpg", fileformat=wx.BITMAP_TYPE_JPEG):
        # get the size of the canvas
        width, height = self.GetSize()

        # create a Bitmap to hold the screenshot
        screenshot = wx.EmptyBitmap(width, height)

        winDC = wx.ClientDC(self)

        memDC = wx.MemoryDC(screenshot)

        # copy the canvas to the bitmap
        memDC.Blit( 0, 0, width, height, winDC, 0, 0)
    
        # save the screenshot
        screenshot.SaveFile(filename, fileformat);


