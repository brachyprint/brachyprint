
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
A sphere primitive.
'''

from __future__ import division

from mesh import Vector
from math import sqrt


def add_sphere(mesh, radius, origin=Vector(0,0,0), model="icosa", detail_level=3):
    '''
    Add a sphere to an existing mesh.

    :param: m -- Mesh() object
    :param: r -- radius
    :param: origin -- centre of sphere
    :param: detail_level -- number of subdivisions
    '''

    def adjust(v):
        return v.normalise()*radius + origin

    if model=="icosa":

        tau = (1.0 + sqrt(5))/2

        model_vertices = [ 
            Vector(-1.0, 0.0, tau), # 0
            Vector( 1.0, 0.0, tau), # 1
            Vector(-1.0, 0.0,-tau), # 2
            Vector( 1.0, 0.0,-tau), # 3

            Vector( 0.0, tau, 1.0), # 4
            Vector( 0.0, tau,-1.0), # 5
            Vector( 0.0,-tau, 1.0), # 6
            Vector( 0.0,-tau,-1.0), # 7

            Vector( tau, 1.0, 0.0), # 8
            Vector(-tau, 1.0, 0.0), # 9
            Vector( tau,-1.0, 0.0), # 10
            Vector(-tau,-1.0, 0.0)  # 11
            ]

        model_triangles = [ 
            [0,1,4],  [0,4,9],  [9,4,5],  [4,8,5],  [4,1,8],    
            [8,1,10], [8,10,3], [5,8,3],  [5,3,2],  [2,3,7],    
            [7,3,10], [7,10,6], [7,6,11], [11,6,0], [0,6,1], 
            [6,10,1], [9,11,0], [9,2,11], [9,5,2],  [7,11,2]]

    elif model=="octa":

        model_vertices = [
            Vector(-1.0, 0.0, 0.0), #0
            Vector( 1.0, 0.0, 0.0), #1
            Vector( 0.0,-1.0, 0.0), #2
            Vector( 0.0, 1.0, 0.0), #3
            Vector( 0.0, 0.0,-1.0), #4
            Vector( 0.0, 0.0, 1.0), #5
            ]

        model_triangles = [(0,2,4),(0,5,2),(0,4,3),(0,3,5),(1,4,2),(1,2,5),(1,3,4),(1,5,3)]

    else:

        raise ValueError("Unrecognised model")

    # vertices associated to a vertex of the model
    vvertices = [mesh.add_vertex(adjust(v)) for v in model_vertices]

    # vertices associated to an edge of the model
    evertices = {}
    for (i,j,k) in model_triangles:
        for (m,n) in [(i,j),(j,k),(k,i)]:
            if (n,m,detail_level-1,1) in evertices:
                continue
            for r in xrange(1,detail_level):
                s = detail_level - r
                evertices[(m,n,r,s)] = mesh.add_vertex(adjust(model_vertices[m]*r + model_vertices[n]*s))

    # vertices associated to a face, and finally the faces themselves
    for (i,j,k) in model_triangles:

        fvertices = {}
        for r in xrange(1,detail_level-1):
            for s in xrange(1,detail_level-r):
                t = detail_level - r - s
                fvertices[(r,s,t)] = mesh.add_vertex(adjust(model_vertices[i]*r + model_vertices[j]*s + model_vertices[k]*t))
        for r in xrange(1,detail_level):
            s = detail_level - r
            if (i,j,r,s) in evertices:
                fvertices[(r,s,0)] = evertices[(i,j,r,s)]
            else:
                fvertices[(r,s,0)] = evertices[(j,i,s,r)]
            if (j,k,r,s) in evertices:
                fvertices[(0,r,s)] = evertices[(j,k,r,s)]
            else:
                fvertices[(0,r,s)] = evertices[(k,j,s,r)]
            if (k,i,r,s) in evertices:
                fvertices[(s,0,r)] = evertices[(k,i,r,s)]
            else:
                fvertices[(s,0,r)] = evertices[(i,k,s,r)]
        fvertices[(detail_level,0,0)] = vvertices[i]
        fvertices[(0,detail_level,0)] = vvertices[j]
        fvertices[(0,0,detail_level)] = vvertices[k]

        for r in xrange(0,detail_level):
            for s in xrange(0,detail_level-r):
                t = detail_level-r-s-1
                mesh.add_face(fvertices[(r+1,s,t)],fvertices[(r,s+1,t)],fvertices[(r,s,t+1)])

        for r in xrange(0,detail_level-1):
            for s in xrange(0,detail_level-r-1):
                t = detail_level-r-s-2
                mesh.add_face(fvertices[(r,s+1,t+1)],fvertices[(r+1,s,t+1)],fvertices[(r+1,s+1,t)])

    for v in mesh.vertices:
        print v
