from mesh import Mesh
from mesh.plane import line_intersection_and_proportion, ParallelLinesException, LinesDoNotCrossException
from mesh import fileio

def intersect(mesh1, mesh2):
    m = combine(mesh1, True, mesh2, True)
    return m

def union(mesh1, mesh2):
    m = combine(mesh1, False, mesh2, False)
    return m
    
def combine(mesh1, inverted1, mesh2, inverted2, tolerance = 0.000001):
    class FaceRemoveException(Exception):
        pass
    possible_overlaps = list(mesh1.possible_face_collisions(mesh2))
    
    replaced_faces1 = {}
    replaced_faces2 = {}
    print "Mesh1", mesh1.vertices
    print "Mesh2", mesh2.vertices
    print len(possible_overlaps)
    n=40
    m=300
    while possible_overlaps:
        face1, face2 = possible_overlaps.pop()
        assert n > 0
        assert m > 0
        try:
            if replaced_faces1.has_key(face1):
                for new_face1 in replaced_faces1[face1]:
                    possible_overlaps.append((new_face1, face2))
                raise FaceRemoveException
            if replaced_faces2.has_key(face2):
                for new_face in replaced_faces2[face2]:
                    possible_overlaps.append((face1, new_face))
                raise FaceRemoveException
            if face1.normal.cross(face2.normal).magnitude() < tolerance and abs(face1.normal.dot(face1.vertices[0]) - face1.normal.dot(face2.vertices[0])) < tolerance: 
                for vertex1 in face1.vertices:
                    if point_in_face(vertex1, face2, tolerance) and vertex1 not in mesh2.vertices:
                        vertex2 = mesh2.add_vertex(vertex1.x, vertex1.y, vertex1.z)
                        possible_overlaps.append((face1, face2)) #There may be more than one face intersection for this pair of points
                        replaced_faces2[face2] = mesh2.split_face(vertex2, face2)
                        raise FaceRemoveException
                for vertex2 in face2.vertices:
                    if point_in_face(vertex2, face1, tolerance) and vertex2 not in mesh1.vertices:
                        vertex1 = mesh1.add_vertex(vertex2.x, vertex2.y, vertex2.z)
                        possible_overlaps.append((face1, face2)) #There may be more than one face intersection for this pair of points
                        replaced_faces1[face1] = mesh1.split_face(vertex1, face1)
                        raise FaceRemoveException      
        except FaceRemoveException:
            m = m - 1
    possible_overlaps = list(mesh1.possible_face_collisions(mesh2))
    replaced_faces1 = {}
    replaced_faces2 = {}
    print "Mesh1", mesh1.vertices
    print "Mesh2", mesh2.vertices
    print len(possible_overlaps)
    fileio.write_ply(mesh1, "/home/martin/m1.ply")
    fileio.write_ply(mesh2, "/home/martin/m2.ply")
    n=40
    m=300
    while possible_overlaps:
        face1, face2 = possible_overlaps.pop()
        fileio.write_ply(mesh1, "/home/martin/m1.ply")
        fileio.write_ply(mesh2, "/home/martin/m2.ply")
        assert n > 0
        assert m > 0
        try:
            if replaced_faces1.has_key(face1):
                for new_face1 in replaced_faces1[face1]:
                    if replaced_faces2.has_key(face2):
                        for new_face2 in replaced_faces2[face2]:
                            possible_overlaps.append((new_face1, new_face2))
                    else:
                        possible_overlaps.append((new_face1, face2))
                raise FaceRemoveException
            if replaced_faces2.has_key(face2):
                for new_face in replaced_faces2[face2]:
                    possible_overlaps.append((face1, new_face))
                raise FaceRemoveException
            if face1.normal.cross(face2.normal).magnitude() < tolerance and abs(face1.normal.dot(face1.vertices[0]) - face1.normal.dot(face2.vertices[0])) < tolerance: 
              for edge1 in face1.edges:
                for edge2 in face2.edges:
                    try:
                        ip, s1, s2 = line_intersection_and_proportion((edge1.v1, edge1.v2), (edge2.v1, edge2.v2))
                        #print "Lines Cross?", edge1.v1, edge1.v2, edge2.v1, edge2.v2, ip, s1, s2
                        if s1 > tolerance and 1-s1 > tolerance and s2 > tolerance and 1- s2 > tolerance:
                            n = n -1
                            #print "Crossed", edge1, edge2, s1, s2, ip
                            faces1_to_be_replaced = edge1.faces()
                            new_vertex1 = mesh1.add_vertex(ip)
                            new_faces1 = mesh1.split_edge(new_vertex1, edge1)
                            for face1_to_be_replaced in faces1_to_be_replaced:
                                replaced_faces1[face1_to_be_replaced] = new_faces1
                            faces2_to_be_replaced = edge2.faces()
                            new_vertex2 = mesh2.add_vertex(ip)
                            origvol = mesh2.volume()
                            new_faces2 = mesh2.split_edge(new_vertex2, edge2)
                            if abs(origvol - mesh2.volume()) > tolerance:
                                #print ip, s1, s2
                                assert False
                            for face2_to_be_replaced in faces2_to_be_replaced:
                                replaced_faces2[face2_to_be_replaced] = new_faces2
                            print "EDGE SPLIT"
                            raise FaceRemoveException
                    except (ParallelLinesException, LinesDoNotCrossException): 
                        pass  
        except FaceRemoveException:
            m = m - 1
#    possible_overlaps = list(mesh1.possible_face_collisions(mesh2))
#    replaced_faces1 = {}
#    replaced_faces2 = {}
#    while possible_overlaps:
 #       face1, face2 = possible_overlaps.pop()
#        try:
#            if replaced_faces1.has_key(face1):
#                for new_face in replaced_faces1[face1]:
#                    possible_overlaps.append((new_face, face2))
#                raise FaceRemoveException
#            if replaced_faces2.has_key(face2):
#                for new_face in replaced_faces2[face2]:
#                    possible_overlaps.append((face1, new_face))
#                raise FaceRemoveException
#            for edge1 in face1.edges:
#                for edge2 in face2.edges:
#                    try:
#                        ip, s1, s2 = line_intersection_and_proportion((edge1.v1, edge1.v2), (edge2.v1, edge2.v2))
#                        if s1 > tolerance and 1-s1 > tolerance and s2 > tolerance and 1-s2 > tolerance:
#                            print edge1, edge2, s1, s2
#                            faces1_to_be_replaced = edge1.faces()
#                            new_vertex1 = mesh1.add_vertex(ip)
#                            new_faces1 = mesh1.split_edge(new_vertex1, edge1)
#                            for face1_to_be_replaced in faces1_to_be_replaced:
#                                replaced_faces1[face1_to_be_replaced] = new_faces1
#                            faces2_to_be_replaced = edge2.faces()
#                            new_vertex2 = mesh2.add_vertex(ip)
#                            new_faces2 = mesh2.split_edge(new_vertex2, edge2)
#                            for face2_to_be_replaced in faces2_to_be_replaced:
#                                replaced_faces2[face2_to_be_replaced] = new_faces2
#                            raise FaceRemoveException
#                    except ValueError:
#                        pass    
#        except FaceRemoveException:
#            pass
    #fileio.write_stl(mesh1, "/home/martin/m1.ply")
    #fileio.write_stl(mesh2, "/home/martin/m2.ply")
    print "M1V", mesh1.vertices
    print "M1V", mesh1.vertices
    print "M1F", len(mesh1.faces)
    print "M2F", len(mesh2.faces)
    print "M1Vol", mesh1.volume()#Check mesh is closed
    print "M2Vol", mesh2.volume()#Check mesh is closed
    m = Mesh()
    vertex1_map = {}
    for v in mesh1.vertices:
        new_vertex = m.get_vertex(v)
        if new_vertex is None: #Vertex does not exist
            new_vertex = m.add_vertex(v.x, v.y, v.z)
        vertex1_map[v] = new_vertex
    for face in mesh1.faces:
        vertices = [vertex1_map[vertex] for vertex in face.vertices]
        if mesh2.contains_point(face.centroid() + face.normal * tolerance * {True: -1, False: 1}[inverted1]) != (not inverted2):
            if inverted1:
                m.add_triangle_face(vertices[0], vertices[2], vertices[1])
            else:
                m.add_triangle_face(vertices[0], vertices[1], vertices[2])
    vertex2_map = {}
    for v in mesh2.vertices:
        new_vertex = m.get_vertex(v)
        #print "?", m.get_vertex(v), m.get_vertex(v.x, v.y, v.z), v.x, v.y, v.z	
        if new_vertex is None: #Vertex does not exist
            #print "Adding"
            new_vertex = m.add_vertex(v.x, v.y, v.z)
            #print "added"
        vertex2_map[v] = new_vertex
    edge_splits = {}
    for face in mesh2.faces:
        vertices = [vertex2_map[vertex] for vertex in face.vertices]
        if mesh1.contains_point(face.centroid() + face.normal * tolerance * {True: -1, False: 1}[inverted2]) != (not inverted1):
            if inverted2:
                add_splits_and_face(m, vertices[0], vertices[2], vertices[1], edge_splits)      
            else:
                add_splits_and_face(m, vertices[0], vertices[1], vertices[2], edge_splits)
    #clean up verticies
    m.clean()
    
    fileio.write_ply(m, "/home/martin/m3.ply")
    return m
    
def add_splits_and_face(m, v0, v1, v2, edge_splits):
    for candidate_face in v0.faces:
        #print candidate_face.vertices, (v0, v1, v2), candidate_face.vertices == (v0, v1, v2), candidate_face.vertices == (v1, v2, v0), candidate_face.vertices == (v2, v0, v1), candidate_face.vertices == (v0, v2, v1), candidate_face.vertices == (v1, v0, v2), candidate_face.vertices == (v2, v1, v0)
        if candidate_face.vertices == (v0, v1, v2) or candidate_face.vertices == (v1, v2, v0) or candidate_face.vertices == (v2, v0, v1): #Duplicate face
            return
        if candidate_face.vertices == (v0, v2, v1) or candidate_face.vertices == (v1, v0, v2) or candidate_face.vertices == (v2, v1, v0): #Duplicate face inverted
            m.remove_face(candidate_face)
            return
    edges = []
    for vs, ve in [(v0, v1), (v1, v2), (v2, v0)]:
        try:
            e = m.get_edge(vs, ve)
            if e.has_two_faces() and not edge_splits.has_key(e):
                new_vertex = m.add_vertex((vs.x + ve.x) / 2, (vs.y + ve.y) / 2, (vs.z + ve.z) / 2)
                edge_splits[e] = new_vertex
            edges.append(e)
        except KeyError:
            edges.append(None) #Edge has not been created yet, and thus does not need splitting
    add_face_with_splits(m, v0, v1, v2, edges, edge_splits)
    
def add_face_with_splits(m, v0, v1, v2, edges, edge_splits):
    #print edge_splits, edges[0], edge_splits.has_key(edges[0]), edges[1], edge_splits.has_key(edges[1]), edges[2], edge_splits.has_key(edges[2])
    if edge_splits.has_key(edges[0]):
        add_face_with_splits(m, v0, edge_splits[edges[0]], v2, [None, None, edges[2]], edge_splits)
        add_face_with_splits(m, edge_splits[edges[0]], v1, v2, [None, edges[1], None], edge_splits)
        return
    if edge_splits.has_key(edges[1]):
        add_face_with_splits(m, v0, v1, edge_splits[edges[1]], [edges[0], None, None], edge_splits)
        add_face_with_splits(m, v0, edge_splits[edges[1]], v2, [None, None, edges[2]], edge_splits)
        return   
    if edge_splits.has_key(edges[2]):
        add_face_with_splits(m, edge_splits[edges[2]], v1, v2, [None, edges[1], None], edge_splits)
        add_face_with_splits(m, v0, v1, edge_splits[edges[2]], [edges[0], None, None], edge_splits)
        return   
    f = m.add_triangle_face(v0, v1, v2)
    
def point_in_face(vertex, face, tolerance):
    u = face.vertices[1] - face.vertices[0]
    v = face.vertices[2] - face.vertices[0]
    w = u.cross(v)
    if abs(w.dot(vertex) - w.dot(face.vertices[0])) > tolerance:
        return False
    p = vertex - face.vertices[0]
    b = p.cross(u).dot(w) / v.cross(u).dot(w)
    a = p.cross(v).dot(w) / u.cross(v).dot(w)
    #print vertex, face.vertices, a, b, tolerance < a < 1 - tolerance and tolerance < b < 1 - tolerance and a + b < 1 - tolerance
    return tolerance < a < 1 - tolerance and tolerance < b < 1 - tolerance and a + b < 1 - tolerance
