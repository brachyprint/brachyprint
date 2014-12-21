
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
Classes to work with collections of rois and convert them into OpenGL
display objects.
'''

from OpenGL.GL import *
from OpenGL.GLUT import *

from OpenGL.arrays import vbo

import numpy as np
from math import pi, acos

from settings import *


class RoiCollection(object):
    '''
    A class to store a collection of rois.
    '''
    def __init__(self, d=[]):
        self.rois = d
        self.current = None

    def clear(self):
        self.rois = []

    def items(self):
        return self.rois
    
    def keys(self):
        raise AttributeError("'list' object has no keys")

    def add_roi(self, r):
        self.rois.append(r)
        return len(self.rois) - 1

    def remove_roi(self, r):
        self.rois.remove(r)

    def __getitem__(self, it):
        return self.rois[it]

COLOURS = {"red": (1,0.2,0.2), "green": (0.2, 1,0.2), "blue":(0.2,0.2,1),}


class RoiCollectionDisplay(RoiCollection):
    '''
    A class to extend roi collections to add OpenGL display.
    '''
    def __init__(self, d=[]):
        self.clear()

        super(RoiCollectionDisplay, self).__init__(d)

        #for name in d.keys():
        #    self.style[name] = "Red"
        #    self.visible[name] = True
        #    self.vertices[name] = False

        # XXX:
        self.visible = True


    def clear(self):
        super(RoiCollectionDisplay, self).clear()

        self.displayObjects = None

        # OpenGL display lists

    def add_roi(self, r):
        i = super(RoiCollectionDisplay, self).add_roi(r)

        # clear display object cache
        self.displayObjects = None

        return i

    def remove_roi(self, r):
        super(RoiCollectionDisplay, self).remove_roi(r)

        # clear display object cache
        self.displayObjects = None


    def setVisible(self, visible):
        self.visible = visible


    def get_display_objects(self):
        if len(self.rois) == 0:
            return []
        #if self.displayObjects is None:
        self._build_display_objects()
        return self.displayObjects


    def _build_display_objects(self):
        '''Build a list of display objects based on the rois in the collection.
        '''

        objs = []

        #for key, roi in self.rois.items():
        for roi in self.rois:
            sphere_list = self.compile_sphere_list(roi)
            line_list = self.compile_line_list(roi)

            obj = {}
            obj["matrix_mode"] = GL_PROJECTION
            obj["style"] = "Red"
            obj["visible"] = self.visible
            obj["list"] = sphere_list
            objs.append(obj)

            obj = {}
            obj["matrix_mode"] = GL_MODELVIEW
            obj["style"] = "Red"
            obj["visible"] = self.visible
            obj["list"] = line_list
            objs.append(obj)

        self.displayObjects = objs


    def compile_sphere_list(self, roi):
        sphere_list = glGenLists(1)
        name = 0
        self.pointlookup = []
        glNewList(sphere_list, GL_COMPILE)
        glMatrixMode(GL_MODELVIEW)
        for roi in self.rois:
            for i, sphere in enumerate(roi.points):
                glPushMatrix()
                glPushName(name)
                self.pointlookup.append((roi, i))
                name = name + 1
                glTranslatef(sphere[0], sphere[1], sphere[2])
                glColor3f(*COLOURS[roi.colour])
                glutSolidSphere(5 * roi.thickness, 10, 10)
                glPopName()
                glPopMatrix()
            # highlight a selected point
            #if roi.current_point_index is not None:
            #    sphere = roi.points[roi.current_point_index]
            #    glPushMatrix()
            #    glTranslatef(sphere[0], sphere[1], sphere[2])
            #    glColor3f(1,1,1)
            #    glutSolidSphere(6 * roi.thickness, 11, 11)
            #    glPopMatrix()
        glEndList()

        return sphere_list


    def compile_line_list(self, roi):
        line_list = glGenLists(1)
        name = 0
        self.linelookup = []
        glNewList(line_list, GL_COMPILE)

        glColor3f(*COLOURS[roi.colour])
        for index, path_list in enumerate(roi.paths):
            glPushName(name)
            for path in path_list:
                self.linelookup.append((roi, index))
                name = name + 1
                p = list(path.points())
                ps = zip(p, p[1:])
                for start, end in ps:
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
                        glutSolidSphere(2 * roi.thickness, 10, 10)
                        glutSolidCylinder(2 * roi.thickness, -length_d, 20 ,20)
                        glPopMatrix()
            glPopName() 
        glEndList()

        return line_list


