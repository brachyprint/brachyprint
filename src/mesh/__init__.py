"""
Mesh
====

Provides
  1. A 3D Vector<> class
  2. A mesh data structure for efficient mesh operations
  3. Functions to create 3D primitives (e.g. cylinders, spheres, cubes)
  4. Mesh manipulations, e.g. clipping, inside/outside, intersection

Available subpackages
---------------------
primitives
    primitive generators
manipulate
    mesh manipulations

Utilities
---------
tests
    Run mesh unittests

"""

from core import *
from plane import *

# subpackages
import primitives
import manipulate

