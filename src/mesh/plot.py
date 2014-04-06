"""
Functions to plot 2d geometry.
"""

from mesh import Vector, Face

import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches


def add_patch(ax, verts):

    if isinstance(verts[0], Vector):
        verts = [(v.x, v.y) for v in verts]
    elif isinstance(verts, Face):
        verts = [(v.x, v.y) for v in verts.vertices]

    codes = [Path.MOVETO] + [Path.LINETO]*(len(verts)-1) + [Path.CLOSEPOLY]

    minx = min([x for (x,y) in verts])
    maxx = max([x for (x,y) in verts])
    miny = min([y for (x,y) in verts])
    maxy = max([y for (x,y) in verts])

    verts = verts + [(0., 0.)]

    path = Path(verts, codes)

    patch = patches.PathPatch(path, facecolor='orange', lw=2, alpha=0.5)
    ax.add_patch(patch)

    return [(minx, maxx), (miny, maxy)]
    

def plot_verts(verts, plot3d=False):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    minx = float('inf')
    maxx = -float('inf')
    miny = float('inf')
    maxy = -float('inf')

    for vs in verts:
        [(minx2, maxx2), (miny2, maxy2)] = add_patch(ax, vs)
        maxx = max(maxx, maxx2)
        minx = min(minx, minx2)
        maxy = max(maxy, maxy2)
        miny = min(miny, miny2)

    ax.set_xlim(minx - (abs(maxx)+abs(minx))*0.1, maxx + (abs(maxx)+abs(minx))*0.1)
    ax.set_ylim(miny - (abs(miny)+abs(maxy))*0.1, maxy + (abs(maxy)+abs(miny))*0.1)

    plt.show()


