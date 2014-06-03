
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

from mesh import Vector

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from OpenGL.GL import shaders
from OpenGL.arrays import vbo

from OpenGL import extensions

import numpy as np

from math import ceil, floor


class pickPixel:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __call__(self):
        gluPickMatrix(self.x, self.y, 1, 1, glGetIntegerv(GL_VIEWPORT))


class MeshCanvas(glcanvas.GLCanvas):
    def __init__(self, parent):
        self.parent = parent
        self.controller = None

        # The magic WX_GL_DEPTH_SIZE argument is required to guarantee
        # initialisation of a depth buffer on the GL canvas. This is needed
        # with certain graphics drivers, e.g. Intel, which allow creation of
        # a GL canvas without a depth buffer (??).
        # 
        # See:
        # https://groups.google.com/forum/#!topic/wxpython-users/lbzhzaBNkxQ
        #   for a discussion.

        attribs = [glcanvas.WX_GL_DOUBLEBUFFER,
                   glcanvas.WX_GL_DEPTH_SIZE,16,]

        # XXX: 16 is a magic number. IsDisplaySupported() should be used to
        # check the attribute list is supported, but it is only available in
        # wxPython >= 2.9. In any case, 24 might be a better choice.

        glcanvas.GLCanvas.__init__(self, parent, -1, attribList=attribs, style= wx.FULL_REPAINT_ON_RESIZE)

        self.init = False

        self.displayObjects = None

        # bind the relevant events
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

        # FIXME: this is a hack to enable highlighting of triangles
        self.highlight = None

    def setController(self, controller):
        '''Set the controller class for the view (MVC pattern).
        '''
        self.controller = controller

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

        self.Update()

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
        '''Initialise OpenGL.
        '''

        glutInit()
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)

        # XXX: this might be a good optimisation to consider enabling
        #glEnable(GL_CULL_FACE)
        #glCullFace(GL_BACK)

        # enable two sided lighting, but not available with all graphics drivers
        if extensions.hasGLExtension("GL_VERTEX_PROGRAM_TWO_SIDE_ARB"):
            glEnable(GL_VERTEX_PROGRAM_TWO_SIDE_ARB)

        # basic vertex shader that adds configurable ambient and diffuse (normal aligned) lighting
        VERTEX_SHADER = shaders.compileShader("""#version 120
            uniform vec3 Light_location;
            uniform vec4 Global_ambient;
            uniform vec4 Light_diffuse;
            uniform vec4 Base_colour;
            attribute vec3 Vertex_position;
            attribute vec3 Vertex_normal;

            void main() {
                gl_Position = gl_ModelViewProjectionMatrix * vec4( Vertex_position, 1.0 );

                vec3 normal = normalize(gl_NormalMatrix * Vertex_normal);
                vec3 lightDir = normalize(vec3(Light_location));
                float NdotL = max(dot(normal, lightDir), 0.0);

                //vec4 diffuse = vec4(0.2,0.2,0.2,1.0);
                vec4 diffuse = Light_diffuse;

                vec4 lighting = NdotL * diffuse + Global_ambient;

                gl_FrontColor = clamp(Base_colour * lighting, 0.0, 1.0);
                //gl_BackColor = clamp(0.5*Base_colour * lighting, 0.0, 1.0);
                gl_BackColor = vec4(0.7, 0.2, 0.2, 0.5);

            }
            """, GL_VERTEX_SHADER)

        FRAGMENT_SHADER = shaders.compileShader("""#version 120

            void main() {

                gl_FragColor = gl_Color;

            }
            """, GL_FRAGMENT_SHADER)

        self.shader = shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)

        # configure uniform variables to pass to the vertex shaders
        for uniform in ( 'Global_ambient', 'Light_location','Light_diffuse', 'Base_colour' ):
            location = glGetUniformLocation( self.shader, uniform )

            if location in (None,-1):
                print 'Warning, no uniform: %s'%( uniform )

            setattr( self, uniform+ '_loc', location )

        for attribute in ( 'Vertex_position','Vertex_normal', ):
            location = glGetAttribLocation( self.shader, attribute )

            if location in (None,-1):
                print 'Warning, no attribute: %s'%( uniform )

            setattr( self, attribute+ '_loc', location )

        glInitNames()

        if self.controller:
            self.controller.InitGL()

        # ensure depth testing is enabled
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)
        glDepthFunc(GL_LEQUAL)
        glDepthRange(0.0, 1.0)

    def OnDraw(self):
        '''Redraw the widget.
        '''
        # clear color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.setupScene()

        for obj in self.displayObjects:
            #obj = self.displayObjects[k]
            glMatrixMode(obj["matrix_mode"])
            style = obj["style"]
            if style == "Red":
                glColor3f(1.0, 0.7, 0.7)
            elif style == "Blue":
                glColor3f(0.7, 0.7, 1.0)
            else:
                glColor3f(1.0, 1.0, 1.0)

            visible = obj["visible"]
            if not visible:
                continue
            
            if "list" in obj:
                glCallList(obj["list"])

        if self.controller.showgrid:
            self.drawXAxisGrid()
            self.drawYAxisGrid()
            self.drawZAxisGrid()


        shaders.glUseProgram(self.shader)
        try:
            glUniform4f( self.Global_ambient_loc, .3,.3, .3, 0.5)
            glUniform4f(self.Light_diffuse_loc, 0.5, 0.5, 0.5, 0.5)
            glUniform3f(self.Light_location_loc, 0, 1, 10)

            for obj in self.displayObjects:

                visible = obj["visible"]
                
                if not visible:
                    continue

                if not "vbo" in obj:
                    continue

                vbo = obj["vbo"]
                num_triangles = obj["vbo_len"]

                if not self.highlight:
                    highlight = False
                else:
                    highlight = True
                    highlight_index = self.highlight_index

                vbo.bind()
                try:
                    style = obj["style"]
                    if style == "Grey":
                        glUniform4f(self.Base_colour_loc, 0.7, 0.7, 0.7, 0.5)
                    elif style == "Red":
                        glUniform4f(self.Base_colour_loc, 0.7, 0.3, 0.3, 0.5)
                    elif style == "Blue":
                        glUniform4f(self.Base_colour_loc, 0.3, 0.3, 0.7, 0.5)
                    else:
                        glUniform4f(self.Base_colour_loc, 0.7, 0.7, 0.7, 0.5)

                    glEnableVertexAttribArray( self.Vertex_position_loc )
                    glEnableVertexAttribArray( self.Vertex_normal_loc )
                    stride = 24
                    glVertexAttribPointer(self.Vertex_position_loc, 3, GL_FLOAT, False, stride, vbo)

                    glVertexAttribPointer(self.Vertex_normal_loc, 3, GL_FLOAT, False, stride, vbo+12)

                    if not highlight:
                        glDrawArrays(GL_TRIANGLES, 0, num_triangles)
                    else:
                        if highlight_index == 0:
                            glUniform4f(self.Base_colour_loc, 0.2, 0.2, 0.2, 0.5)
                            glDrawArrays(GL_TRIANGLES, 0, 3)
                            glUniform4f(self.Base_colour_loc, 0.7, 0.7, 0.7, 0.5)
                            glDrawArrays(GL_TRIANGLES, 3, num_triangles-3)
                        elif highlight_index == num_triangles-2:
                            glUniform4f(self.Base_colour_loc, 0.2, 0.2, 0.2, 0.5)
                            glDrawArrays(GL_TRIANGLES, 0, num_triangles-3)
                            glUniform4f(self.Base_colour_loc, 0.7, 0.7, 0.7, 0.5)
                            glDrawArrays(GL_TRIANGLES, num_triangles-3, 3)
                        else:
                            glUniform4f(self.Base_colour_loc, 0.7, 0.7, 0.7, 0.5)
                            glDrawArrays(GL_TRIANGLES, 0, highlight_index)
                            glDrawArrays(GL_TRIANGLES, highlight_index+3, num_triangles-highlight_index-3)
                            glUniform4f(self.Base_colour_loc, 0.2, 0.2, 0.2, 0.5)
                            glDrawArrays(GL_TRIANGLES, highlight_index, 3)

                finally:
                    vbo.unbind()
                    glDisableVertexAttribArray( self.Vertex_position_loc )
                    glDisableVertexAttribArray( self.Vertex_normal_loc )
        finally:
            shaders.glUseProgram(0)

        self.SwapBuffers()

    def updateViewPort(self, selector = lambda: None):
        '''Update the view port.
        '''
        if self.GetContext():
            self.SetCurrent()
            glViewport(0, 0, self.viewport.width, self.viewport.height)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            selector()

            xscale = self.viewport.xscale()
            yscale = self.viewport.yscale()
            range_max = self.viewport.range_max
            if range_max == float('inf'):
                return
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
        rangey = [self.controller.meshes.min_Y, self.controller.meshes.max_Y]
        rangez = [self.controller.meshes.min_Z, self.controller.meshes.max_Z]
        self.drawGrid(rangex, rangey, rangez, d)

    def drawYAxisGrid(self, d=10):
        rangex = [self.controller.meshes.min_X, self.controller.meshes.max_X]
        rangey = []
        rangez = [self.controller.meshes.min_Z, self.controller.meshes.max_Z]
        self.drawGrid(rangex, rangey, rangez, d)

    def drawZAxisGrid(self, d=10):
        rangex = [self.controller.meshes.min_X, self.controller.meshes.max_X]
        rangey = [self.controller.meshes.min_Y, self.controller.meshes.max_Y]
        rangez = []
        self.drawGrid(rangex, rangey, rangez, d)

    def calcGridSize(self, numLines=10):
        rangex = [self.controller.meshes.min_X, self.controller.meshes.max_X]
        rangey = [self.controller.meshes.min_Y, self.controller.meshes.max_Y]
        rangez = [self.controller.meshes.min_Z, self.controller.meshes.max_Z]

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


