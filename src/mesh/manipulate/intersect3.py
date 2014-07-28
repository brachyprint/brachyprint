"""for each face1 in mesh1
  for each face1 in mesh2
    if face1 and face2 intersect
      find new edge
      add vertices
      split up triangles
      while the edge crosses to new faces
        follow edge to next face
        find new edge
        add vertices
        split up triangles

for each face in mesh1
   if appropriate add face to new mesh
for each face in mesh2
   if appropriate add face to new mesh"""

import numpy
from ..core import Vertex

def split(mesh1, mesh2):
    meshcopy1 = mesh1.copy()
    meshcopy2 = mesh2.copy()
    meshcopy1.ensure_fresh_octrees()
    meshcopy2.ensure_fresh_octrees()
    subdivide_meshes(meshcopy2, meshcopy1)
    #subdivide_meshes(meshcopy1, meshcopy2)
    meshcopy1.ensure_fresh_octrees()
    meshcopy2.ensure_fresh_octrees()
    return meshcopy1, meshcopy2
    
def subdivide_meshes(mesh1, mesh2):
    mesh2.ensure_fresh_octrees()
    for face1 in mesh1.faces:
        for edge1 in face1.edges:
            for refernce_pont, bounding_box, face2 in mesh2.face_octree.intersect_with_line_segment(edge1.v1, edge1.v2):
                intersection = face_intersects_with_edge(face2, edge1)
                if intersection is not None and intersection not in [edge1.v1, edge1.v2]:
                    vertex, new_faces1, new_faces2 = split_at_intersection(mesh1, mesh2, intersection, edge1, face2)
                    propagate_split(vertex, new_faces1, new_faces2, mesh1, mesh2, vertex, True)
                    return None

def split_at_intersection(mesh1, mesh2, intersection, edge1, face2):
    vertex = Vertex(intersection.x, intersection.y, intersection.z)
    assert vertex not in [edge1.v1, edge1.v2]
    mesh1.add_specific_vertex(vertex)
    new_faces1 = mesh1.split_edge(vertex, edge1)
    mesh2.add_specific_vertex(vertex)
    new_faces2 = mesh2.split_face(vertex, face2)
    for nf2 in new_faces2:
        assert nf2 in mesh2.faces
    return vertex, new_faces1, new_faces2

def face_intersects_with_edge(face, edge):
    """Determines whether an edge and a face intersect, and returns the intersection point as a vector"""
    #consider the equation for a line p = d * l + l0, where l is the edge displacement and l0 is edge.v1
    #combine this with the a plane (p-p0).n = 0 where n is face.normal and p0 is face.vertices[0]
    #this give d = (p0 - l0).n / l.n
    edge_displacement = edge.displacement()
    l_dot_n = edge_displacement.dot(face.normal)
    if l_dot_n:
        d = (face.vertices[0] - edge.v1).dot(face.normal) / l_dot_n
        if 0 < d < 1: # line-plane intersection is within the linesegment
            p = d * edge_displacement + edge.v1
            # consider the plane p = p0 + a * (p1 - p0) + b * (p2 - p0) where (p0, p1, p2) = face.vertices
            # cross with (p1 - p0) gives b = (p-p0)^(p1-p0) / (p2-p0)^(p1-p0)
            b = div_parallel_vectors((p-face.vertices[0]).cross(face.vertices[1]-face.vertices[0]),
                                     (face.vertices[2]-face.vertices[0]).cross(face.vertices[1]-face.vertices[0]))
            # cross with (p2 - p0) gives a = (p-p0)^(p2-p0) / (p1-p0)^(p2-p0)
            a = div_parallel_vectors((p-face.vertices[0]).cross(face.vertices[2]-face.vertices[0]),
                                     (face.vertices[1]-face.vertices[0]).cross(face.vertices[2]-face.vertices[0]))
            if a > 0 and b > 0 and a + b < 1: # line-plane intersection is within face
                return p
        
def div_parallel_vectors(v1, v2):
    """Divides two parellel vectors (preserving sign)"""
    return v1.dot(v2) / v2.dot(v2)

def propagate_split(vertex, faces1, faces2, mesh1, mesh2, origin, first_propogation):
    """Propagates a split from vertex"""
    for f1 in faces1:
        for f2 in faces2:
            opp_edge2 = f2.opposite_edge(vertex)
            if not ((origin in [opp_edge2.v1, opp_edge2.v2]) and origin in f1.vertices):
                intersection = face_intersects_with_edge(f1, opp_edge2)
                if intersection is not None and intersection not in [opp_edge2.v1, opp_edge2.v2]:
                    vertex, new_faces2, new_faces1 = split_at_intersection(mesh2, mesh1, intersection, opp_edge2, f1)
                    propagate_split(vertex, new_faces1, new_faces2, mesh1, mesh2, origin, False)
                    return None
            opp_edge1 = f1.opposite_edge(vertex)
            if not ((origin in [opp_edge1.v1, opp_edge1.v2]) and origin in f2.vertices):
                intersection = face_intersects_with_edge(f2, opp_edge1)
                if intersection is not None and intersection not in [opp_edge1.v1, opp_edge1.v2]:
                    vertex, new_faces1, new_faces2 = split_at_intersection(mesh1, mesh2, intersection, opp_edge1, f2)
                    propagate_split(vertex, new_faces1, new_faces2, mesh1, mesh2, origin, False)
                    return None  

def get_verticies(faces):
    vs = []
    for f in faces:
        for v in f.vertices:
            vs.append(v)
    return vs

    

