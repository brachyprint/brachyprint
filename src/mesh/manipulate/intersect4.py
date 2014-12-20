from mesh import Mesh

def intersect(mesh1, mesh2):
    m, face1_map, face2_map = combine(mesh1, True, mesh2, True)
    for original1_face, new_faces in face1_map.items():
        for new_face in new_faces:
            c = new_face.centroid()
            if not mesh2.contains_point(c):
                m.remove_face(new_face)
    for original2_face, new_faces in face2_map.items():
        for new_face in new_faces:
            c = new_face.centroid()
            if not mesh1.contains_point(c):
                m.remove_face(new_face)
    return m

def combine(mesh1, inverted1, mesh2, inverted2):
    m = Mesh()
    vertex1_map = dict((v, m.add_vertex(v.x, v.y, v.z)) for v in mesh1.vertices)
    face1_map = {}
    for face in mesh1.faces:
        face1_map[face] = []
        vertices = [vertex1_map[vertex] for vertex in face.vertices]
        if inverted1:
            f = m.add_triangle_face(vertices[0], vertices[2], vertices[1])
        else:
            f = m.add_triangle_face(vertices[0], vertices[1], vertices[2])
        face1_map[face].append(f)
    vertex2_map = dict((v, m.add_vertex(v.x, v.y, v.z)) for v in mesh2.vertices)
    face2_map = {}
    for face in mesh2.faces:
        face2_map[face] = []
        vertices = [vertex2_map[vertex] for vertex in face.vertices]
        if inverted2:
            f = m.add_triangle_face(vertices[0], vertices[2], vertices[1])
        else:
            f = m.add_triangle_face(vertices[0], vertices[1], vertices[2])
        face2_map[face].append(f)
    return m, face1_map, face2_map
