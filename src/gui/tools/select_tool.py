
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
A GUI tool for selecting the part of a mesh delineated by some regions of interest (ROIs).
'''


from gui_tool import GuiTool
import wx
from gui import Roi

from settings import *

import mesh
from octrees import Octree
from points import expand, make_ply

from OpenGL.GL import *
from OpenGL.GLUT import *


class SelectTool(GuiTool):

    def __init__(self, name):
        super(SelectTool, self).__init__(name)


    def initDisplay(self):
        self.current_roi = None
        self.current_point_index = None


    def getSubTools(self):
        if self.roi.has_key("onSelect"):
            return ["Edit " + self.name, "Select " + self.name]
        else:
            return ["Edit " + self.name]


    def getDisplayObjects(self):

        return []


    def findMesh(self):
        # find the mesh under the mouse
        hits = []
        for name in self.controller.meshes.keys():
            hit = self.controller.hit_mesh(name)
            if hit:
                hits.append((hit[0]**2+hit[1]**2+hit[2]**2, hit[3], hit, name))

        if not hits:
            return None, None

        hits = sorted(hits, key=lambda x: x[0])
        
        hit = hits[0]
        meshname = hit[3]
        hit = hit[2]

        return (meshname, hit)


    def OnMouseDown(self, x, y, lastx, lasty, event):
        if event.LeftIsDown():

            meshname, face_hit = self.findMesh()

            if not meshname: # click did not fall on a mesh
                return False
            if face_hit:
                x, y, z, triangle_name = face_hit
                triangle = self.controller.meshes[meshname].faces[triangle_name]
                self.onSelect(triangle, self.controller.meshes[meshname], self.controller.meshes.rois[meshname])

            return True

        return False


    def get_avoidance_edges(self, rois):
        avoid_edges = []

        for roi in rois:
            paths = sum(roi.paths, [])
            edges = sum([path.get_edges() for path in paths], [])
            #Make list of edges to avoid.  Where there is a point in the middle of a triangle, an extra edge needs to be found.
            #such that a full ring of avoidance edges is created.
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
            print "VERTEX", vertex
            #Go around the loop of edges, adding them to the avoidance list, and adding extra edges where necessary.
            for i, edge in enumerate(edges):
                print i
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
                            avoid_edges.append(edge)
                            vertex = edge.v2
                            break
                        elif extra_edge.v1 == vertex and extra_edge.v2 == edge.v2:
                            avoid_edges.append(extra_edge)
                            avoid_edges.append(edge)
                            vertex = edge.v1
                            break
                        elif extra_edge.v2 == vertex and extra_edge.v1 == edge.v1:
                            avoid_edges.append(extra_edge)
                            avoid_edges.append(edge)
                            vertex = edge.v2
                            break
                        elif extra_edge.v2 == vertex and extra_edge.v1 == edge.v2:
                            avoid_edges.append(extra_edge)
                            avoid_edges.append(edge)
                            vertex = edge.v1
                            break
                    else:
                        assert False
                        avoid_edges.append(edge)
        return avoid_edges


    def onSelect(self, triangle, m, rois):

        # XXX:
        self.base_file = "blahblah"

        avoid_edges = self.get_avoidance_edges(rois)
        #Save the cut out mesh to a file
        roughcut = m.cloneSubVol(triangle, avoid_edges)

        self.controller.addMesh(roughcut, "Rough")

        self.controller.parent.meshPanel.addMesh("Rough")
        self.controller.parent.meshPanel.hideMesh("Skin")

        return

        print "Saving"
        mesh.fileio.write_ply(roughcut, self.base_file + "rough.ply")



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
        make_ply(points, self.base_file + "external_base", poisson_depth = POISSON_DEPTH)

        print "Done"


