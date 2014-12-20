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
A class representing a region of interest (ROI) defined on the surface of a
mesh.
'''


from copy import copy


COLOURS = {"red": (1,0.2,0.2), "green": (0.2, 1,0.2), "blue":(0.2,0.2,1),}


class Roi:
    def __init__(self, meshname, mesh, closed, colour="green", thickness = 1):
        self.paths = []
        self.points = []

        self.meshname = meshname
        self.mesh = mesh

        self.closed = closed

        self.colour = colour
        self.thickness = thickness


    def new_point(self, x, y, z, face_name, end, index=None):
        # if index is supplied, insert a point at index
        if index is not None:
            self.points = self.points[:index + 1] + [(x, y, z, face_name)] + self.points[index+1:]
            temp = copy(self.paths)
            self.paths = temp[:index] + [None, None] + temp[index+1:]
            ret_index = index + 1
        elif end:
            self.points.append((x, y, z, face_name))
            if len(self.points) > 1:
                self.paths.append(None)
            ret_index = len(self.points) - 1
        else:
            self.points = [(x, y, z, face_name)] + self.points
            if len(self.points) > 1:
                self.paths = [None] + self.paths
            ret_index = 0

        # update any affected paths
        self._update()

        # return the index of the new point
        return ret_index


    def complete(self):
        """Complete the ROI (i.e. join the last point to the first)
        """

        assert self.being_drawn() == True
        if self.closed == True:
            self.paths.append(None)
            self._update()


    def being_drawn(self):
        return len(self.points) == 0 or len(self.paths) < len(self.points)


    def is_empty(self):
        return len(self.points) == 0


    def is_last(self, i):
        return i == len(self.points) - 1


    def is_end_point(self, i):
        return i == len(self.points) - 1 or i == 0


    def is_complete(self):
        return len(self.points) >= 3 and len(self.paths) == len(self.points)


    def remove_point(self, i):
        """Remove the point at the specified index. Adjust any affected paths.
        """

        if i > 0:
            if i < len(self.paths):
                self.paths =  self.paths[:i - 1] + [None] +  self.paths[i + 1:]
            else:
                self.paths =  self.paths[:i - 1]
        else:
            if len(self.paths) == len(self.points):
                self.paths =  self.paths[1:-1] + [None]
            else:
                self.paths =  self.paths[1:]
        self.points = self.points[:i] + self.points[i + 1:]
        self._update()


    def move_point(self, i, x, y, z, face_name):
        """Move the point at the specified index to a new location. Adjust any affected paths.
        """

        self.points[i] = (x, y, z, face_name)
        if i > 0:
            self.paths[i - 1] = None
        else:
            if not self.being_drawn():
                self.paths[-1] = None
        if i < len(self.paths):
            self.paths[i] = None
        else:
            if not self.being_drawn():
                self.paths[0] = None
        self._update()


    def _update(self):
        """Recalculate the paths between points.
        """

        for index, path in enumerate(self.paths):
            if path is None:
                if index + 1 < len(self.points):
                    self.paths[index] = self.mesh.get_path(self.points[index], self.points[index + 1])
                else:
                    self.paths[index] = self.mesh.get_path(self.points[index], self.points[0])



############# TO REMOVE BELOW THIS LINE ################

#<<<<<<< Updated upstream
#class RoiGUI(object):
#    def __init__(self, mesh, meshname, closed, colour="green", thickness = 1, onSelect=None):
#        self.meshname = meshname
#        self.mesh = mesh
#=======
class RoiGUI:
    def __init__(self, closed, colour="green", thickness = 1, onSelect=None):
        #self.meshname = meshname
        #self.mesh = mesh
#>>>>>>> Stashed changes
        self.closed = closed
        self.onSelect = onSelect

        self.current_point_index = None
        self.pointlookup = []
        self.linelookup = []
        self.colour = colour
        self.thickness = thickness


    def new_roi(self, meshname):
        r = ROI(meshname)
        self.rois.append(r)
        return r

    def new_point(self, x, y, z, face_name, meshname, end = True, index=None):
        print "Start", index
        if not self.current_roi:
            r = self.new_roi(meshname)
            self.current_roi = r
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


    def get_avoidance_edges(self):
        avoid_edges = []
        for roi in self.rois:
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
