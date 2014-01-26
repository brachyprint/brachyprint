from __future__ import division
from os import listdir
from os.path import isfile, join
from subprocess import call
import dicom
import numpy
from octrees.octrees import Octree
import os, os.path
from math import sin, cos, pi, asin
import wx
from settings import *
from points import copy_point_cloud_excluding, makepoints, save, load, make_ply

if __name__ == '__main__':
    app = wx.App(False)        
    openDirDialog = wx.DirDialog(None, "Open", DEFAULT_INPUT_DIR, wx.DD_DIR_MUST_EXIST)
    openDirDialog.ShowModal()
    path = openDirDialog.GetPath()
    openDirDialog.Destroy()
    seriesInstanceUIDs = {}
    for f in listdir(path):
        if isfile(join(path,f)):
            d = dicom.read_file(join(path,f)) 
            seriesInstanceUIDs[d.SeriesInstanceUID] = "%s - %s - %s - %s" % (d.Modality, d.PatientsName, d.StudyDescription, d.SeriesDescription)
            del d
    series = seriesInstanceUIDs.items()
    seriesDialog = wx.SingleChoiceDialog(None, "Choose Series", "Series", [s[1] for s in series])
    seriesDialog.ShowModal()
    seriesUID = series[seriesDialog.GetSelection()][0]
    seriesDialog.Destroy()

    openFileDialog = wx.FileDialog(None, "Save", DEFAULT_OUTPUT_DIR, DEFAULT_OUTPUT_FILE, "", wx.FD_SAVE)
    openFileDialog.ShowModal()
    output_base = openFileDialog.GetPath()
    openFileDialog.Destroy()

    points = load(path, seriesUID, [500, 1200], SAMPLING)
    #Make clean skin point cloud by removing any skin points (density 500) that are near bone/metal points (density 12000)
    clean_skin = copy_point_cloud_excluding(points[500], points[1200], 2)
    
    #Run Poisson reconstruction alogrithem on point clouds
    #make_ply(points[500], output_base + ".skin", poisson_depth = POISSON_DEPTH)
    make_ply(clean_skin, output_base + ".skin", poisson_depth = POISSON_DEPTH)
    make_ply(points[1200], output_base + ".bone", poisson_depth = POISSON_DEPTH)

