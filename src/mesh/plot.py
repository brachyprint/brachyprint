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

"""
Functions to plot 2d geometry.
"""

from mesh import Vector, Face
from mesh import Vector2d, Vertex2d

import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches


def add_patch(ax, verts, plot_points, plot3d, u1, u2):

    if isinstance(verts, Face):
        verts = [(v.x, v.y) for v in verts.vertices]
    elif isinstance(verts[0], Vector):
        if plot3d:
            verts = [v.project2d(u1, u2) for v in verts]
        else:
            verts = [(v.x, v.y) for v in verts]
    elif isinstance(verts[0], Vector2d) or isinstance(verts[0], Vertex2d):
        verts = [(v.x, v.y) for v in verts]

    codes = [Path.MOVETO] + [Path.LINETO]*(len(verts)-1) + [Path.CLOSEPOLY]

    minx = min([x for (x,y) in verts])
    maxx = max([x for (x,y) in verts])
    miny = min([y for (x,y) in verts])
    maxy = max([y for (x,y) in verts])

    verts = verts + [(0., 0.)]

    path = Path(verts, codes)

    patch = patches.PathPatch(path, facecolor='orange', lw=2, alpha=0.5)
    ax.add_patch(patch)

    if plot_points:
        ax.plot(*zip(*verts), marker='o', color='r', ls='')

    return [(minx, maxx), (miny, maxy)]
    

def plot_verts(verts, plot_points=True, plot3d=False):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    minx = float('inf')
    maxx = -float('inf')
    miny = float('inf')
    maxy = -float('inf')

    u1=None
    u2=None
    if isinstance(verts[0][0], Vector) and plot3d:
        u1 = verts[0][1] - verts[0][0]
        u2 = verts[0][2] - verts[0][0]
        n = u1.cross(u2)
        u2 = n.cross(u1)
        u1.normalise()
        u2.normalise()

    for vs in verts:
        [(minx2, maxx2), (miny2, maxy2)] = add_patch(ax, vs, plot_points, plot3d, u1, u2)
        maxx = max(maxx, maxx2)
        minx = min(minx, minx2)
        maxy = max(maxy, maxy2)
        miny = min(miny, miny2)

    ax.set_xlim(minx - (abs(maxx)+abs(minx))*0.1, maxx + (abs(maxx)+abs(minx))*0.1)
    ax.set_ylim(miny - (abs(miny)+abs(maxy))*0.1, maxy + (abs(maxy)+abs(miny))*0.1)

    plt.show()


