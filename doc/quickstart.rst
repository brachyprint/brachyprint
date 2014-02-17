Quick start 
===========

Requirements
------------

* pydicom -- DICOM manipulation library: https://code.google.com/p/pydicom
* triangle -- triangulation library: http://dzhelil.info/triangle/
* PyOpenGL -- python wrapper for OpenGL: http://pyopengl.sourceforge.net
* wxPython -- python wrapper for wxWidgets: http://wxpython.org



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

