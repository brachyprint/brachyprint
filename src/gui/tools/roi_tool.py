
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
A GUI tool for editing and selecting regions of interest (ROIs).
'''


from gui_tool import GuiTool
import wx
from gui import RoiGUI

from OpenGL.GL import *

class opengl_list:
    def __init__(self, list_):
        self.list = list_
    def __call__(self):
        glCallList(self.list)


class RoiTool(GuiTool):

    def __init__(self, name, roi):
        super(RoiTool, self).__init__(name)

        self.roi = roi

    def initDisplay(self):
        # create an RoiGUI associated with the tool
        self.roiGUI = RoiGUI(mesh = self.controller.meshes[self.roi["meshname"]], **self.roi)
        self.roiGUI.InitGL()

    def getSubTools(self):
        if self.roi.has_key("onSelect"):
            return ["Edit " + self.name, "Select " + self.name]
        else:
            return ["Edit " + self.name]

    def select(self, subtool):
        self.mode = subtool

    def getDisplayObjects(self):

        objs = {}
        key = self.name
        objs[key+"_spheres"] = {}
        objs[key+"_spheres"]["matrix_mode"] = GL_MODELVIEW
        objs[key+"_spheres"]["style"] = "Red"
        objs[key+"_spheres"]["visible"] = True
        objs[key+"_spheres"]["list"] = self.roiGUI.sphere_list
        objs[key+"_lines"] = {}
        objs[key+"_lines"]["matrix_mode"] = GL_MODELVIEW
        objs[key+"_lines"]["style"] = "Red"
        objs[key+"_lines"]["visible"] = True
        objs[key+"_lines"]["list"] = self.roiGUI.line_list

        return objs

    def OnKeyPress(self, keycode, event):
        if keycode == wx.WXK_DELETE:
            roiGUI = self.roiGUI
            if roiGUI.current_roi is not None and roiGUI.current_point_index is not None:
                if len(roiGUI.current_roi.points) == 1:
                    roiGUI.rois.remove(roiGUI.current_roi) 
                else:
                    roiGUI.current_roi.remove_point(roiGUI.current_point_index)
                roiGUI.current_roi = None
                roiGUI.current_point_index = None
                roiGUI.update()
                return True
        elif keycode == wx.WXK_ESCAPE:
            roiGUI = self.roiGUI
            roiGUI.current_roi = None
            roiGUI.current_point_index = None
            roiGUI.update()
            return True
        return False

    def OnMouseDown(self, x, y, lastx, lasty, event):
        if event.LeftIsDown():
            if self.mode == 0:
                roiGUI = self.roiGUI
                sphere_hits = self.controller.view.hit(x, y, opengl_list(roiGUI.sphere_list), roiGUI.sphere_list_length())
                line_hits = self.controller.view.hit(x, y, opengl_list(roiGUI.line_list), roiGUI.line_list_length())
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
                    face_hit = self.controller.hit_location(roiGUI.meshname)
                    if face_hit:
                        x, y, z, triangle_name = face_hit
                        roiGUI.current_roi = roi
                        roiGUI.new_point(x, y, z, triangle_name, index = index)
                        roiGUI.update()
                else:
                    face_hit = self.controller.hit_location(roiGUI.meshname)
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
            elif self.mode == 1:
                roiGUI = self.roiGUI
                face_hit = self.controller.hit_location(roiGUI.meshname)
                if face_hit:
                    x, y, z, triangle_name = face_hit
                    triangle = self.controller.meshes[roiGUI.meshname].faces[triangle_name]
                    roiGUI.onSelect(roiGUI, triangle)
        return False

