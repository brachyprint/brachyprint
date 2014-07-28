
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


'''
A cuboid primitive.
'''

from __future__ import division

from mesh import Vector, nullVector



def add_cuboid(mesh,
               lx=1, ly=1, lz=1,
               nx=1, ny=1, nz=1,
               vx=Vector(1,0,0), vy=Vector(0,1,0), vz=Vector(0,0,1),
               corner=nullVector):
    """Add a cuboid (or more generally, a parallelepiped), to an existing
    mesh.

    Arguments:

    - lx, ly, and lz denote the sidelengths, expressed in multiples of
      the basis vectors vx, vy and vz (see below). These default to 1.

    - nx, ny, and nz denote the number of edges into which to
      subdivide the cuboid edges. These default to 1.

    - vx, vy, and vz denote the edge vectors. These default to the
      standard basis vectors.

    - corner denotes the vector where the first corner shall be
      places. This defaults to zero.
    """

    vx = Vector(vx)
    vy = Vector(vy)
    vz = Vector(vz)
    corner = Vector(corner)

    vertices = {}
    def make_vertex(i,j,k):
        vertices[(i,j,k)] = mesh.add_vertex(corner + vx*(lx*i/nx) + vy*(ly*j/ny) + vz*(lz*k/nz))
    for i in xrange(nx+1):
        for j in xrange(ny+1):
            if i not in [0,nx] and j not in [0,ny]:
                make_vertex(i,j,0)
                make_vertex(i,j,nz)
            else:
                for k in xrange(nz+1):
                    make_vertex(i,j,k)

    for i in xrange(nx):
        for j in xrange(ny):
            mesh.add_face(vertices[(i,j,0)],vertices[(i+1,j,0)],vertices[(i,j+1,0)])
            mesh.add_face(vertices[(i,j+1,0)],vertices[(i+1,j,0)],vertices[(i+1,j+1,0)])
            mesh.add_face(vertices[(i,j,nz)],vertices[(i,j+1,nz)],vertices[(i+1,j,nz)])
            mesh.add_face(vertices[(i,j+1,nz)],vertices[(i+1,j+1,nz)],vertices[(i+1,j,nz)])

    for j in xrange(ny):
        for k in xrange(nz):
            mesh.add_face(vertices[(0,j,k)],vertices[(0,j+1,k)],vertices[(0,j,k+1)])
            mesh.add_face(vertices[(0,j,k+1)],vertices[(0,j+1,k)],vertices[(0,j+1,k+1)])
            mesh.add_face(vertices[(nx,j,k)],vertices[(nx,j,k+1)],vertices[(nx,j+1,k)])
            mesh.add_face(vertices[(nx,j,k+1)],vertices[(nx,j+1,k+1)],vertices[(nx,j+1,k)])
            
    for i in xrange(nx):
        for k in xrange(nz):
            mesh.add_face(vertices[(i,0,k)],vertices[(i,0,k+1)],vertices[(i+1,0,k)])
            mesh.add_face(vertices[(i+1,0,k)],vertices[(i,0,k+1)],vertices[(i+1,0,k+1)])
            mesh.add_face(vertices[(i,ny,k)],vertices[(i+1,ny,k)],vertices[(i,ny,k+1)])
            mesh.add_face(vertices[(i+1,ny,k)],vertices[(i+1,ny,k+1)],vertices[(i,ny,k+1)])
