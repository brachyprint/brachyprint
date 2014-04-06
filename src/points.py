
from __future__ import division
from os import listdir
from os.path import isfile, join
from subprocess import call
import dicom
import numpy
from octrees import Octree
import os, os.path
from math import sin, cos, pi, asin
from settings import *
from mesh import Vector


def makepoints(t, zpositions, posX, posY, spacingX, spacingY, level):
    t = t.astype(numpy.int16)
    mean = (t[1:, 1:, 1:]  + t[1:, 1:, :-1]  + t[1:, :-1, 1:]  + t[1:,:-1,:-1] 
          + t[:-1, 1:, 1:] + t[:-1, 1:, :-1] + t[:-1, :-1, 1:] + t[:-1,:-1,:-1]) / 8
    gz =   (t[1:, 1:, 1:]  + t[1:, 1:, :-1]  + t[1:, :-1, 1:]  + t[1:,:-1,:-1] \
          - t[:-1, 1:, 1:] - t[:-1, 1:, :-1] - t[:-1, :-1, 1:] - t[:-1,:-1,:-1]) / 4
    #print "gz", gz
    gy =   (t[1:, 1:, 1:]  + t[1:, 1:, :-1]  - t[1:, :-1, 1:]  - t[1:,:-1,:-1] \
          + t[:-1, 1:, 1:] + t[:-1, 1:, :-1] - t[:-1, :-1, 1:] - t[:-1,:-1,:-1]) / 4
    
    gx =   (t[1:, 1:, 1:]  - t[1:, 1:, :-1]  + t[1:, :-1, 1:]  - t[1:,:-1,:-1] \
          + t[:-1, 1:, 1:] - t[:-1, 1:, :-1] + t[:-1, :-1, 1:] - t[:-1,:-1,:-1]) / 4
    #print t[:2, :2, :2]
    #print mean[:1, :1, :1]
    #print "gx", gx[:1, :1, :1]
    #print "gy", gy[:1, :1, :1]
    #print "gz", gz.dtype
    #print ((posX, posX + (t.shape[0] + 1) * spacingX),(posY, posY + (t.shape[1] + 1) * spacingY),(min(zpositions),max(zpositions)))
    results = Octree(((posX, posX + (t.shape[2] + 1) * spacingX),(posY, posY + (t.shape[1] + 1) * spacingY),(min(zpositions),max(zpositions))))
    #del t
    gn = (gx ** 2 + gy ** 2 + gz ** 2) ** 0.5
    nx = gx / gn
    #print nx.dtype
    #print gx.dtype
    del gx
    ny = gy / gn
    del gy
    nz = gz / gn
    del gz
    dist = (mean - level) / gn
    del gn
    dx = dist * nx
    dy = dist * ny
    dz = dist * nz
    print dz.dtype
    del dist
    hit = numpy.logical_and(numpy.logical_and(abs(dx) < 0.5, abs(dy) < 0.5), abs(dz) < 0.5)
    for i, j, k in zip(*hit.nonzero()):
        rx = nx[i, j, k] / spacingX
        ry = ny[i, j, k] / spacingY
        rz = nz[i, j, k] / float(zpositions[i+1] - zpositions[i])
        rn = (rx ** 2 + ry ** 2 + rz ** 2) ** 0.5
        rx = -rx / rn
        ry = -ry / rn
        rz = -rz / rn
        #print k, dx[i, j, k], posX, spacingX, t.shape
        #print posX, posX + (k + 0.5 - dx[i, j, k] / 2) * spacingX, posX + (t.shape[0] + 1) * spacingX
        results.insert((posX + (k + 0.5 - dx[i, j, k]) * spacingX,
                        posY + (j + 0.5 - dy[i, j, k]) * spacingY,
                        float(zpositions[i]) * (0.5 + dz[i, j, k]) + float(zpositions[i+1]) * (0.5 - dz[i, j, k])),
                        (rx,
                        ry,
                        rz))
    del dx
    del dy
    del dz
    del nx
    del ny
    del nz
    return results

def points_to_string(points):
    r = ""
    for ignore, point, normal in points.by_distance_from_point((0,0,0), 1000):
        r = r + "%f %f %f %f %f %f\n" % (point[0], point[1], point[2], normal[0], normal[1], normal[2])
    return r

def load(mypath, myseries, levels, sampling):
    dicomfiles = []
    for f in listdir(mypath):
        if isfile(join(mypath,f)):
            try:
                dicomfiles.append(dicom.read_file(join(mypath,f)))
            except:
                print "%s is not a DICOM file" % f
    mySlices = []
    for d in dicomfiles:
        try:
            if d.SeriesInstanceUID == myseries:
                mySlices.append(d)
        except:
            None
    del dicomfiles
    def cmpZ(x, y):
        return cmp(x.ImagePositionPatient[2], y.ImagePositionPatient[2])
    mySlices.sort(cmpZ)
    d=[]
    for s in mySlices:
        a = numpy.fromstring(s.PixelData, dtype=numpy.uint16)
        a.resize(s.Rows, s.Columns)
        r = 0
        for i in range(sampling):
            for j in range(sampling):
                r = r + a[i::sampling, j::sampling]
        d.append(r / sampling ** 2)
    del r
    exampleSlice = mySlices[0]
    zpositions = [float(s.ImagePositionPatient[2]) for s in mySlices[::sampling]]
    del mySlices
    ts = numpy.array(d)
    t = 0
    for k in range(sampling):
        t = t + ts[k:k - sampling - ts.shape[0] % sampling:sampling]
    del ts
    t = t / sampling
    del d
    return dict([(level, 
                 makepoints(t, 
                      zpositions, 
                      float(exampleSlice.ImagePositionPatient[0]), 
                      float(exampleSlice.ImagePositionPatient[1]),
                      float(exampleSlice.PixelSpacing[0] * sampling),
                      float(exampleSlice.PixelSpacing[1] * sampling),
                      level)) for level in levels])

def save(points, outfile):
    f = open(outfile, "w")
    f.write(points_to_string(points))
    f.close()

def poisson(infile, outfile, poisson_depth = 8):
    call([POISSON_RECONSTRUCTOR_EXECUTABLE, "--in", infile, "--out", outfile, "--depth", str(poisson_depth)])

def make_ply(points, filenamebase, poisson_depth = 8):
    plt_filename = filenamebase + ".plt" #Maybe this should be a temporary file
    ply_filename = filenamebase + ".ply"
    save(points, plt_filename)
    poisson(plt_filename, ply_filename, POISSON_DEPTH)

def copy_point_cloud_excluding(points, excluding_points, distance):
    clean_skin = Octree(points.bounds)
    points_list = points.by_distance_from_point((0,0,0)) #Points do not actually need to be ordered, perhaps they can be found more efficiently
    for ignore, point, normal in points_list:
        try:
            excluding_points.by_distance_from_point(point, distance).next()
        except StopIteration:
            clean_skin.insert(point, normal)
    return clean_skin

def expand_bounds(((xl, xu), (yl, yu), (zl, zu)), distance):
    return ((xl - distance, xu + distance), (yl - distance, yu + distance), (zl - distance, zu + distance))

BASIS_VECTORS = [Vector(0,0,1), Vector(0,1,0), Vector(1,0,0)]

def expand(points, distance):
    expanded = Octree(expand_bounds(points.bounds, distance))
    points_list = list(points)
    d_angle = 0.2
    max_angle = 0.600000001
    all_norm_offsets = [(0, 0, 1)]
    distance_slightly_reduced = 0.99 * distance
    for theta in [d_angle * (i + 1) for i in range(int(max_angle / d_angle))]:
        sin_theta = sin(theta)
        cos_theta = cos(theta)
        num_phis = int(round(2 * pi * sin_theta / d_angle))
        for phi in [2 * pi * j / num_phis for j in range(num_phis)]:
            all_norm_offsets.append((sin(theta) * cos(phi), sin(theta) * sin(phi), cos(theta)))
    num_points = len(points_list) 
    hits = 0
    for i, (point, normal) in enumerate(points_list):
        if i % 100 == 0:
            print "%0.2f%% complete of %i hits from %i starting points" % ((100.0 * i) / num_points, hits, i)

        new_point = [p + n * distance for p, n in zip(point, normal)]
        expanded.insert(new_point, normal)
    return expanded
