from __future__ import division
from os import listdir
from os.path import isfile, join
from subprocess import call
import dicom
import numpy
from octrees.octrees import Octree

sampling = 4
POISSON_DEPTH = 4

mypath = "redfred"
myseries = "1.2.840.113704.1.111.3736.1370522307.4"
out = r"output/redfredc"
poissionrec = "PoissonRecon/Bin/Linux/PoissonRecon"

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

def load(mypath, myseries, levels):
    dicomfiles = [ dicom.read_file(join(mypath,f)) for f in listdir(mypath) if isfile(join(mypath,f)) ]
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

def poission(infile, outfile, poisson_depth = 8):
    call([poissionrec, "--in", infile, "--out", outfile, "--depth", str(poisson_depth)])

if __name__ == '__main__':
    points = load(mypath, myseries, [500, 1200])
    #Make clean skin point cloud by removing any skin points (density 500) that are near bone/metal points (density 12000)
    clean_skin = Octree(points[500].bounds)
    for ignore, point, normal in points[500].near_point((0,0,0), 1000):
        try:
            points[1200].near_point(point, 2).next()
        except StopIteration:
            clean_skin.insert(point, normal)
    
    skinpointsfile = out + "500.plt"
    bonepointsfile = out + "1200.plt"
    cleanskinpointsfile = out + "clean.plt"
    save(points[500], skinpointsfile)
    poission(skinpointsfile, out + "skin.ply", POISSON_DEPTH)
    save(clean_skin, cleanskinpointsfile)
    poission(cleanskinpointsfile, out + "clean.ply", POISSON_DEPTH)
    save(points[1200], bonepointsfile)
    poission(bonepointsfile, out + "bone.ply", POISSON_DEPTH)

