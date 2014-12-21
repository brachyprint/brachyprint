
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
A GUI tool for editing and selecting regions of interest (ROIs).
'''


from gui_tool import GuiTool
import wx
from gui import Roi

from OpenGL.GL import *
from OpenGL.GLUT import *


class RoiTool(GuiTool):

    def __init__(self, name, roi):
        super(RoiTool, self).__init__(name)

        self.roi = roi


    def initDisplay(self):
        self.current_roi = None
        self.current_point_index = None


    def getSubTools(self):
        if self.roi.has_key("onSelect"):
            return ["Edit " + self.name, "Select " + self.name]
        else:
            return ["Edit " + self.name]


    def select(self, subtool):
        self.mode = subtool


    def deselect(self):
        self.current_roi = None
        self.current_point_index = None
        self.controller.Refresh()


    def getDisplayObjects(self):
        objs = []

        # highlight a selected point
        if self.current_roi is not None and self.current_point_index is not None:
            roi = self.current_roi

            # build a display list
            sphere_list = glGenLists(1)
            glNewList(sphere_list, GL_COMPILE)
            glMatrixMode(GL_MODELVIEW)

            sphere = roi.points[self.current_point_index]
            glPushMatrix()
            glTranslatef(sphere[0], sphere[1], sphere[2])
            glColor3f(1,1,1)
            glutSolidSphere(6 * roi.thickness, 11, 11)
            glPopMatrix()
            glEndList()

            obj = {}
            obj["matrix_mode"] = GL_PROJECTION
            obj["style"] = "Red"
            obj["visible"] = True
            obj["list"] = sphere_list
            objs.append(obj)

        return objs


    def OnKeyPress(self, keycode, event):
        if keycode == wx.WXK_DELETE:
            roi = self.current_roi
            if roi is not None and self.current_point_index is not None:
                if len(roi.points) == 1: # delete the roi
                    self.controller.meshes.rois[roi.meshname].remove_roi(roi)
                    self.current_point_index = None
                    self.current_roi = None
                else:
                    roi.remove_point(self.current_point_index)
                    self.current_point_index = None
                    self.current_roi = None
                self.controller.Refresh()

                return True

        elif keycode == wx.WXK_ESCAPE:
            self.current_point_index = None
            self.current_roi = None
            self.controller.Refresh()

            return True

        return False


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
            if self.mode == 0: # subtool "lasso"

                if self.current_roi: # currently working on an ROI

                    roi = self.current_roi
                    meshname = roi.meshname

                    sphere_hits = self.controller.hit_roi(self.current_roi)
                    line_hits = None # XXX:

                    # clicked on a sphere
                    if sphere_hits:
                        # if not the first point
                        (index, p) = sphere_hits
                        if roi.being_drawn() and \
                            ((self.current_point_index == 0 and roi.is_last(index)) or \
                             (index == 0 and roi.is_last(self.current_point_index))):
                            roi.complete()

                        # select the point
                        if self.current_point_index == index: # clicked on this point; deselect
                            self.current_point_index = None
                            self.current_roi = None
                        else:
                            self.current_point_index = index

                    # XXX: clicked on a line
                    elif line_hits and roiGUI.current_point_index is None:
                        roi, index =  roiGUI.linelookup[line_hits[0][2][0]]
                        face_hit = self.controller.hit_mesh(meshname)
                        if face_hit:
                            x, y, z, triangle_name = face_hit
                            roiGUI.current_roi = roi
                            roiGUI.new_point(x, y, z, triangle_name, index = index)

                    else:
                        face_hit = self.controller.hit_mesh(meshname)

                        if not face_hit:
                            # user clicked outside the mesh, so deselect the ROI
                            self.current_roi = None
                        else:
                            x, y, z, triangle_name = face_hit
                            if roi.being_drawn() and self.current_point_index == 0: # add a new point to the ROI
                                self.current_point_index = self.current_roi.new_point(x, y, z, triangle_name, False)
                            #elif roi.being_drawn() and roi.is_last(self.current_point_index): # add a new point to the ROI
                            #    self.current_point_index = self.current_roi.new_point(x, y, z, triangle_name, False, self.current_point_index)
                            else: # must be a currently selected point, so move it
                                roi.move_point(self.current_point_index, x, y, z, triangle_name)

                    # tell the controller that there have been changes so it can update the display
                    self.controller.Refresh()

                else:
                    # no roi currently selected
                    meshname, face_hit = self.findMesh()

                    if not meshname: # click did not fall on a mesh
                        return False
                    
                    x, y, z, triangle_name = face_hit

                    sphere_hits = []
                    for roi in self.controller.meshes.rois[meshname]:
                        sphere_hit = self.controller.hit_roi(roi)
                        if sphere_hit:
                            sphere_hits.append((sphere_hit, roi))

                    # click falls on existing point
                    if sphere_hits:
                        # select the point
                        self.current_point_index = sphere_hits[0][0][0]
                        self.current_roi = sphere_hits[0][1]
                    # click falls on existing line
                    #elif line_hit:

                    else:
                        # create a new ROI

                        mesh = self.controller.meshes[meshname]
                        self.current_roi = Roi(meshname, mesh, True, colour=self.roi["colour"], thickness=self.roi["thickness"])
                        roi_index = self.controller.meshes.rois[meshname].add_roi(self.current_roi)
                        self.current_point_index = self.current_roi.new_point(x, y, z, triangle_name, False)

                        # XXX: messy
                        self.controller.parent.meshPanel.addRoi(meshname, "ROI%d" % (roi_index+1))

                    #face_hit = self.controller.hit_mesh(meshname)
                    #if face_hit:
                    #    x, y, z, triangle_name = face_hit
                        #if roiGUI.current_roi is None:
                        #    roiGUI.current_roi = roiGUI.new_roi(meshname)
                    #    if roiGUI.current_roi.being_drawn() and \
                    #       (roiGUI.current_roi.is_last(roiGUI.current_point_index) or roiGUI.current_roi.is_empty()):
                    #        roiGUI.new_point(x, y, z, triangle_name)
                    #    elif roiGUI.current_roi.being_drawn() and \
                    #         roiGUI.current_point_index == 0:
                    #        roiGUI.new_point(x, y, z, triangle_name, end = False)
                    #    elif roiGUI.current_point_index is not None:
                    #        roiGUI.move_point(roiGUI.current_point_index, x, y, z, triangle_name)
                    #else:
                    #    roiGUI.current_point_index = None
                    #    roiGUI.current_roi = None
                    self.controller.Refresh()
                return True

            elif self.mode == 1: # subtool "select"
                roiGUI = self.roiGUI
                face_hit = self.controller.hit_mesh(meshname)
                if face_hit:
                    x, y, z, triangle_name = face_hit
                    triangle = self.controller.meshes[meshname].faces[triangle_name]
                    roiGUI.onSelect(roiGUI, triangle)
        return False

