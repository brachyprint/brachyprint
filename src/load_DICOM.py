from __future__ import division
from os import listdir
from os.path import isfile, join
from subprocess import call
import dicom
import numpy
from octrees import Octree
import os, os.path
from math import sin, cos, pi, asin
import wx
from settings import *
from points import copy_point_cloud_excluding, makepoints, save, load, make_ply
import re

class DicomLoader(object):

    def __init__(self):
        pass
    
    def SelectInputSeries(self):
        openDirDialog = wx.DirDialog(None, "Open", DEFAULT_INPUT_DIR, wx.DD_DIR_MUST_EXIST)
        if openDirDialog.ShowModal() == wx.ID_CANCEL:
            openDirDialog.Destroy()
            return (None, None)

        path = openDirDialog.GetPath()
        openDirDialog.Destroy()
        seriesInstanceUIDs = {}
        for f in listdir(path):
            if isfile(join(path,f)):
                try:
                    d = dicom.read_file(join(path,f)) 
                except dicom.filereader.InvalidDicomError: # ignore invalid DICOM files
                    continue
                seriesInstanceUIDs[d.SeriesInstanceUID] = "%s - %s - %s - %s" % (d.Modality, d.PatientsName, d.StudyDescription, d.SeriesDescription)
                del d
        series = seriesInstanceUIDs.items()
        seriesDialog = wx.SingleChoiceDialog(None, "Choose Series", "Series", [s[1] for s in series])
        if seriesDialog.ShowModal() == wx.ID_CANCEL:
            seriesDialog.Destroy()
            return (None, None)

        seriesUID = series[seriesDialog.GetSelection()][0]
        seriesDialog.Destroy()

        return (path, seriesUID)

    def SelectOutputFile(self):
        openFileDialog = wx.FileDialog(None, "Save", DEFAULT_OUTPUT_DIR, DEFAULT_OUTPUT_FILE, "", wx.FD_SAVE)
        openFileDialog.SetWildcard("PLY files (*.ply)|*.ply")

        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            openFileDialog.Destroy()
            return None

        output_base = openFileDialog.GetPath()
        openFileDialog.Destroy()

        output_base = re.sub('\.(skin|bone)\.ply$', '', output_base)

        # XXX: should there be a confirmation before overwriting an existing file?

        return output_base

if __name__ == '__main__':
    app = wx.App(False)        
    dl = DicomLoader()
    (path, seriesUID) = dl.SelectInputSeries()
    if path == None or seriesUID == None:
        exit()

    output_base = dl.SelectOutputFile()
    if output_base == None:
        exit()

    points = load(path, seriesUID, [500, 1200], SAMPLING)
    #Make clean skin point cloud by removing any skin points (density 500) that are near bone/metal points (density 12000)
    clean_skin = copy_point_cloud_excluding(points[500], points[1200], 2)
    
    #Run Poisson reconstruction alogrithem on point clouds
    #make_ply(points[500], output_base + ".skin", poisson_depth = POISSON_DEPTH)
    make_ply(clean_skin, output_base + ".skin", poisson_depth = POISSON_DEPTH)
    make_ply(points[1200], output_base + ".bone", poisson_depth = POISSON_DEPTH)


