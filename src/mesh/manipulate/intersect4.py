from mesh import Mesh
from mesh.plane import line_intersection_and_proportion

def intersect(mesh1, mesh2):
    m = combine(mesh1, True, mesh2, True)
    return m

def union(mesh1, mesh2):
    m = combine(mesh1, False, mesh2, False)
    return m

def combine(mesh1, inverted1, mesh2, inverted2, tolerance = 0.0000001):
    for face in mesh1.faces:
        for overlapping_face in mesh2.overlapping_coplanar_faces(face):
            for edge1 in face.edges:
                for edge2 in overlapping_face.edges:
                    try:
                        ip, s = line_intersection_and_proportion((edge1.v1, edge1.v2), (edge2.v1, edge2.v2))
                        if abs(s) > tolerance and abs(1-s) > tolerance:
                            pass #assert False  
                    except ValueError:
                        pass
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
        if new_vertex is None: #Vertex does not exist
            new_vertex = m.add_vertex(v.x, v.y, v.z)
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
