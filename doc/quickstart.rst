Quick start 
===========

Requirements
------------

* pydicom -- DICOM manipulation library: https://code.google.com/p/pydicom
  (Debian package: python-dicom)
* triangle -- triangulation library: http://dzhelil.info/triangle/
  (PyPI package: triangle)
* PyOpenGL -- python wrapper for OpenGL: http://pyopengl.sourceforge.net
  (Debian package: python-opengl)
* wxPython -- python wrapper for wxWidgets: http://wxpython.org
  (Debian package: python-wxtools)
* matplotlib -- 2D plotting library for Python: http://matplotlib.org/
  (Debian package: python-matplotlib)

Under Debian Jessie, one author has had some success running the
following (as a superuser):

  aptitude install python-dicom python-pip python-dev cython python-wxtools python-matplotlib python-opengl
  pip install triangle


Building
--------

To build simply run:: 

   cd src
   make
    

Running
-------

To fetch the example data use::
    
   getdata.sh

Then extract the CT data and generate the mesh::

   cd src
   python load_DICOM.py

Select the directory containing the example data, and the series.

Then display the rough mesh for region of interest (ROI) selection::

   python rough.py

