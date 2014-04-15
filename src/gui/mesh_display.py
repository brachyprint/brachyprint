
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
Classes to work with collections of meshes and convert them into OpenGL
display objects.
'''

from OpenGL.GL import *
from OpenGL.GLUT import *

from settings import *

class Range3d(object):
    def __init__(self, minX, maxX, minY, maxY, minZ, maxZ):
        self.min_X = minX
        self.max_X = maxX
        self.min_Y = minY
        self.max_Y = maxY
        self.min_Z = minZ
        self.max_Z = maxZ

    def rangex(self):
        return self.max_X - self.min_X

    def rangey(self):
        return self.max_Y - self.min_Y

    def rangez(self):
        return self.max_Z - self.min_Z

    def meanx(self):
        return (self.min_X + self.max_X) / 2

    def meany(self):
        return (self.min_Y + self.max_Y) / 2

    def meanz(self):
        return (self.min_Z + self.max_Z) / 2

    def range_max(self):
        return (self.rangex() ** 2 + self.rangey() ** 2 + self.rangez() ** 2) ** 0.5


class MeshCollection(Range3d):
    '''
    A class to store a collection of meshes.

    It also computes their extent.
    '''
    def __init__(self, d={}):
        self.meshes = d

        min_X = min([m.minX for m in self.meshes.values()])
        max_X = max([m.maxX for m in self.meshes.values()])
        min_Y = min([m.minY for m in self.meshes.values()])
        max_Y = max([m.maxY for m in self.meshes.values()])
        min_Z = min([m.minZ for m in self.meshes.values()])
        max_Z = max([m.maxZ for m in self.meshes.values()])

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


class MeshCollectionDisplay(MeshCollection):
    '''
    A class to extend mesh collections to add OpenGL display.
    '''
    def __init__(self, d={}):
        super(MeshCollectionDisplay, self).__init__(d)
        self.displayObjects = None

    def add_mesh(self, m, name):
        super(MeshCollectionDisplay, self).add_mesh(m, name)

    def get_display_objects(self):
        if self.displayObjects is None:
            self._build_display_objects()
        return self.displayObjects

    def _build_display_objects(self):
        '''Build a list of display objects based on the meshes in the collection.
        '''
        self.mainList = {}
        self.vertexList = {}
        for key, mesh in self.meshes.items():
            self.mainList[key] = self.faceListInit(mesh)
            self.vertexList[key] = self.vertexListInit(mesh)
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

        self.displayObjects = objs

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

