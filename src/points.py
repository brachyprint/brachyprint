from __future__ import division
from os import listdir
from os.path import isfile, join
from subprocess import call
import dicom
import numpy
from octrees.octrees import Octree
import os, os.path

SAMPLING = 4
POISSON_DEPTH = 4

mypath = "../data/redfred"
myseries = "1.2.840.113704.1.111.3736.1370522307.4"
OUTPUT_DIR = r"../output"
OUTPUT_FILENAME_BASE = "redfred"
poissonrec = "../bin/PoissonRecon"

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
        rz = nz[i, j, k] / (zpositions[i+1] - zpositions[i])
        rn = (rx ** 2 + ry ** 2 + rz ** 2) ** 0.5
        rx = -rx / rn
        ry = -ry / rn
        rz = -rz / rn
        #print k, dx[i, j, k], posX, spacingX, t.shape
        #print posX, posX + (k + 0.5 - dx[i, j, k] / 2) * spacingX, posX + (t.shape[0] + 1) * spacingX
        results.insert((posX + (k + 0.5 - dx[i, j, k]) * spacingX,
                        posY + (j + 0.5 - dy[i, j, k]) * spacingY,
                        zpositions[i] * (0.5 + dz[i, j, k]) + zpositions[i+1] * (0.5 - dz[i, j, k])),
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
    for ignore, point, normal in points.near_point((0,0,0), 1000):
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
    zpositions = [s.ImagePositionPatient[2] for s in mySlices[::sampling]]
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
                      exampleSlice.ImagePositionPatient[0], 
                      exampleSlice.ImagePositionPatient[1],
                      exampleSlice.PixelSpacing[0] * sampling,
                      exampleSlice.PixelSpacing[1] * sampling,
                      level)) for level in levels])

def save(points, outfile):
    f = open(outfile, "w")
    f.write(points_to_string(points))
    f.close()

def poisson(infile, outfile, poisson_depth = 8):
    call([poissonrec, "--in", infile, "--out", outfile, "--depth", str(poisson_depth)])

def make_ply(points, filenamebase, poisson_depth = 8):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    plt_filename = os.path.join(OUTPUT_DIR, filenamebase + ".plt") #Maybe this should be a temporary file
    ply_filename = os.path.join(OUTPUT_DIR, filenamebase + ".ply")
    save(points, plt_filename)
    poisson(plt_filename, ply_filename, POISSON_DEPTH)

def copy_point_cloud_excluding(points, excluding_points, distance):
    clean_skin = Octree(points.bounds)
    points_list = points.by_distance_from_point((0,0,0)) #Points do not actually need to be ordered, perhaps they can be found more efficiently
    for ignore, point, normal in points_list:
        try:
            excluding_points.near_point(point, distance).next()
        except StopIteration:
            clean_skin.insert(point, normal)
    return clean_skin

def expand(points, distance):
    print points.bounds
    clean_skin = Octree(points.bounds)#expand bounds
    points_list = points.by_distance_from_point((0,0,0)) #Points do not actually need to be ordered, perhaps they can be found more efficiently
    for ignore, point, normal in points_list:        
        try:
            points.near_point(point, distance).next()
        except StopIteration:
            clean_skin.insert(point, normal)

if __name__ == '__main__':
    points = load(mypath, myseries, [500, 1200], SAMPLING)
    #Make clean skin point cloud by removing any skin points (density 500) that are near bone/metal points (density 12000)
    clean_skin = copy_point_cloud_excluding(points[500], points[1200], 2)
    #expanded_skin = expand(clean_skin, 10)
    
    #Run Poisson reconstruction alogrithem on point clouds
    make_ply(points[500], OUTPUT_FILENAME_BASE + "skin", poisson_depth = POISSON_DEPTH)
    make_ply(clean_skin, OUTPUT_FILENAME_BASE + "clean", poisson_depth = POISSON_DEPTH)
    make_ply(points[1200], OUTPUT_FILENAME_BASE + "bone", poisson_depth = POISSON_DEPTH)

