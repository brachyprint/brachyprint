
from __future__ import division

from math import sqrt

# http://geomalgorithms.com/a06-_intersect-2.html


# algorithms
#
#  pre-processing:
#   construct the octree of triangles down to a max depth, or until only 1 triangle in each cube
#    for each triangle, insert into the octree
#     at the current octree level, construct the planes for the 8 cubes
#     traverse the octree, comparing the surface with each cube to determine where it lies
#
#  1. point inside object
#    work out which octree node the point is in
#    create a ray to the nearest bounding box edge
#    determine which octree nodes the ray passes through
#     for each triangle in the nodes, count the number of triangles the ray passes through
#    if the number of intersections is odd, the point is inside, otherwise it is outside
#
#  2. intersect two objects
#    determine the overlapping octree nodes


def triangle_segment_intersect(p, vs):
    '''
    Determine if a polygon is intersected by a segment.
    
    p -- two item list of Vectors
    vs -- three item list of Vectors

    Returns:
        -1: triangle degenerate
         0: no intersection
         1: intersection
         2: line is in the plane (i.e. parallel)
    '''
    
    epsilon = .000001
    
    # check for the intersection of the ray and the plane

    u = vs[1] - vs[0]
    v = vs[2] - vs[0]
    n = u.cross(v)
    
    # check if the triangle is degenerate
    if n[0] == 0 and n[1] == 0 and n[2] == 0:
        return -1 # bail out
    
    dirv = p[1] - p[0]
    w0 = p[0] - vs[0]
    a = -n.dot(w0)
    b = n.dot(dirv)
    
    if abs(b) < epsilon:
        if a == 0:
            return 2 # in the plane
        else:
            return 0
    
    r = a/b
    if r < 0 or r > 1: # segment behind or in front of the plane
        return 0
    #if r < 0 or r > 1:
    #    print r
    
    # find the intersection point of the line and the plane
    i = p[0] + r * dirv
    
    # determine if i is inside the triangle T
    uu = u.dot(u)
    uv = u.dot(v)
    vv = v.dot(v)
    w = i - vs[0]
    wu = w.dot(u)
    wv = w.dot(v)
    
    d = uv * uv - uu * vv
    
    s = (uv * wv - vv * wu) / d
    if s < 0.0 or s > 1.0: # I is outside T
        return 0
    t = (uv * wu - uu * wv) / d
    if t < 0.0 or (s + t) > 1.0: # I is outside T
        return 0
    
    # on the boundary of the triangle
    #if s < epsilon or t < epsilon or s + t > 1.0 - epsilon:
    #    return 3

    return i
    return 1 # I is in T

def line_intersect():

    return model.Vector(1,1,1)



def triangle_triangle_intersect(f1, f2):
    
    # intersect f1 with the plane of f2
    s1 = triangle_plane_intersect(f1, f2)

    if isinstance(s1, int): # no intersection
        return 0

    # intersect f2 with the plane of f1
    s2 = triangle_plane_intersect(f2, f1)

    if isinstance(s2, int): # no intersection
        return 0

    if len(s1) < 2 or len(s2) < 2:
        print "hmm"
        return 0

    # given the two intersection lines, determine their overlap

    # determine overlap between two lines

    b = s1[1] - s1[0] # basis vector in axis transformation
    norm = b.dot(b)
    b = b / sqrt(norm)

    d1 = [[],[]]; d2 = [[],[]]
    d1[0] = b.dot(s1[0] - s1[0])
    d1[1] = b.dot(s1[1] - s1[0])
    d2[0] = b.dot(s2[0] - s1[0])
    d2[1] = b.dot(s2[1] - s1[0])

    epsilon = .00001
    if abs(s1[1].cross(s1[0]).dot(s2[0])) > epsilon:
        print "ijkhkj"
    if abs(s1[1].cross(s1[0]).dot(s2[1])) > epsilon:
        print "ijkhkj2"

    #b = s2[1] - s2[0] # basis vector in axis transformation

    #d1 = [[],[]]; d2 = [[],[]]
    #d1[0] = dot(b, s1[0]-s2[0])
    #d1[1] = dot(b, s1[1]-s2[0])
    #d2[0] = dot(b, s2[0]-s2[0])
    #d2[1] = dot(b, s2[1]-s2[0])

    swapped = 0
    if d1[0] > d1[1]:
        d1[0], d1[1] = d1[1], d1[0]
        s1[0], s1[1] = s1[1], s1[0]
        swapped += 1
    
    if d2[0] > d2[1]:
        d2[0], d2[1] = d2[1], d2[0]
        s2[0], s2[1] = s2[1], s2[0]
        swapped += 1

    if d1[0] < d2[0] and d1[1] < d2[0]:
        return 0

    if d1[0] > d2[1] and d1[1] > d2[1]:
        return 0

    if d1[0] < d2[0]:
        if d2[0] > d1[1]:
            return 0

    if d2[0] < d1[0]:
        if d1[0] > d2[1]:
            return 0

#    return s2


    #if d1[0] < d2[0] and d1[1] < d2[0]:
    #    if d2[0] > 0.0 and d2[1] > 0.0:
    #        return 0
    #elif d2[0] < 0.0 and d2[1] < 0.0:
    #    if d1[0] > 0.0 and d1[0] > 0.0:
    #        return 0
        
    s = [[],[]]
    if d1[0] < d2[0]:
        s[0] = s2[0]
    else:
        s[0] = s1[0]

    if d1[1] > d2[1]:
        s[1] = s2[1]
    else:
        s[1] = s1[1]

    # check for a point "intersection"
    if s[1] == s[0]:
        return s[1]

    #if swapped % 2 == 1:
    #    s[0], s[1] = s[1], s[0]
    #print s1
    #print s2
    #print "s="
    #print s
    #if s1[0].z != s1[1].z and s2[0].z == 50:
    #    print "s1="
    #    print s1
    #    print "s2="
    #    print s2

    #    print "s="
    #    print s

    return s


def triangle_plane_intersect(f1, f2):

    epsilon = .00001

    # intersect f1 with the plane of f2
    
    # check for the intersection of the ray and the plane

    u = f2[1] - f2[0]
    v = f2[2] - f2[0]
    n = u.cross(v)

    # check if the triangle is degenerate
    if n[0] == 0 and n[1] == 0 and n[2] == 0:
        print "bail out"
        return -1 # bail out

    intersect = []
    behind = []; front = []
    for i in range(3):
        a = n.dot(f1[i]-f2[0])
        if a < -epsilon:
            # f1[i] is behind the plane
            behind.append(f1[i])
        elif a > epsilon:
            # f1[i] is in front of the plane
            front.append(f1[i])
        else:
            # f1[i] is in the plane
            print f1[i]
            intersect.append(f1[i])
            
    if len(front) == 3 or len(behind) == 3: # no intersection
        return 0

    if len(intersect) == 3:
        return -1

    for i in range(len(front)):
        for j in range(len(behind)):
            a = -n.dot(front[i]-f2[0])
            b = n.dot(behind[j]-front[i])
            r = a/b

            #if r < 0 or r > 1:
            #    print r
    
            intersect.append(front[i] + (behind[j]-front[i])*r)

    return intersect

    
    # check the 3 edges of f1 for intersection with the plane
    p = [[],[]]
    count = 0
    for i in range(3):
        p = [f1[i-1], f1[i]]
        a = -n.dot(p[0]-f2[0])
        b = n.dot(p[1]-p[0])
    
        if abs(b) < epsilon:
            if a == 0:
                return 2 # in the plane
            else:
                return 0
    
    r = a/b
    if r < 0 or r > 1: # segment behind or in front of the plane
        return 0
    
    # find the intersection point of the line and the plane
    i = p[0] + (p[1]-p[0])*r


    return 0


def polygon_plane_clip(vertices,plane):
    boundaryEpsilon = .001
    positive = 0
    negative = 0
    location = {}
    result = {}
    polygonInterior =  1
    polygonBoundary =  0
    polygonExterior = -1

    # basically, the 4th parameter of the plane equation. 
    # not sure if it's index [3] or [4] in python
    planeOriginDistance = plane[3] 

    for a in xrange(len(vertices)):
        d = plane[:3].dot(vertices[a]) + planeOriginDistance;
        if d > boundaryEpsilon:
            location[a] = polygonInterior
            positive += 1
        else:
            if d < -boundaryEpsilon:
                location[a] = polygonExterior
                negative += 1
            else:
                location[a] = polygonBoundary
    if negative == 0:
        for a in xrange(len(vertices)):
            result[a] = vertices[a]
        return result.values()
    elif positive == 0:
        return vertices
    count = 0
    previous = len(vertices) - 1
    for index in xrange(len(vertices)):
        loc = location[index]
        if loc == polygonExterior:
            if location[previous] == polygonInterior:
                v1 = vertices[previous]
                v2 = vertices[index]
                dv = vec_subt(v2,v1)
                
                t = (v2.dot(plane[:3]) + planeOriginDistance) / dv.dot(plane[:3])
                result[count] = vec_subt(v2,sc_vec(t,dv))
                count += 1
        else:
            v1 = vertices[index]
            if loc == polygonInterior and location[previous] == polygonExterior:
                v2 = vertices[previous]
                dv = vec_subt(v2,v1)
                
                t = (v2.dot(plane[:3]) + planeOriginDistance) / dv.dot(plane[:3])
                result[count] = vec_subt(v2,sc_vec(t,dv))
                count += 1

            result[count] = v1
            count += 1
        previous = index
    return result.values()
    
    
