from mesh import Mesh

def intersect(mesh1, mesh2):
    m = combine(mesh1, False, mesh2, False)
    return m

def combine(mesh1, inverted1, mesh2, inverted2):
    m = Mesh()
    vertex1_map = {}
    for v in mesh1.vertices:
        new_vertex = m.get_vertex(v)
        if new_vertex is None: #Vertex does not exist
            new_vertex = m.add_vertex(v.x, v.y, v.z)
        vertex1_map[v] = new_vertex
    for face in mesh1.faces:
        vertices = [vertex1_map[vertex] for vertex in face.vertices]
        if mesh2.contains_point(face.centroid()) != inverted2:
            if inverted1:
                f = m.add_triangle_face(vertices[0], vertices[2], vertices[1])
            else:
                f = m.add_triangle_face(vertices[0], vertices[1], vertices[2])
    vertex2_map = {}
    for v in mesh2.vertices:
        new_vertex = m.get_vertex(v)
        if new_vertex is None: #Vertex does not exist
            new_vertex = m.add_vertex(v.x, v.y, v.z)
        vertex2_map[v] = new_vertex
    for face in mesh2.faces:
        vertices = [vertex2_map[vertex] for vertex in face.vertices]
        if mesh1.contains_point(face.centroid()) != inverted1:
            if inverted2:
                f = m.add_triangle_face(vertices[0], vertices[2], vertices[1])
            else:
                f = m.add_triangle_face(vertices[0], vertices[1], vertices[2])
    return m
