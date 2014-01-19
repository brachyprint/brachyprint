import parseply

class AStar:
    def __init__(self, s1, s2, mesh):
        self.s1 = s1
        self.s2 = s2
        self.t1 = mesh.faces[s1[3]]
        self.t2 = mesh.faces[s2[3]]
        self.d = {}
        for v in self.t1.vertices:
            self.add_node(((v.x - s1[0]) ** 2 + (v.y - s1[1]) ** 2 + (v.z - s1[2]) ** 2) ** 0.5, v)
        while True:
            self.d
    def add_node(self, dist, node):
        if not self.d.has_key(node) or self.d[node][0] > dist:
            self.d[node] = dist, dist + ((node.x - self.s2[0]) ** 2 + (node.y - self.s2[1]) ** 2 + (node.z - self.s2[2]) ** 2) * 0.5
        

class Mesh:
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.edges = {}
        self.maxX, self.minX = None, None
        self.maxY, self.minY = None, None
        self.maxZ, self.minZ = None, None
        self.volumes = {}
        self.next_face_name = 0
        self.next_volume_name = 0
        self.face_to_vol = {}

    def add_vertex(self, x, y, z):
        self.vertices.append(Vertex(x, y, z))
        if self.maxX is None:
            self.maxX = x
            self.minX = x
            self.maxY = y
            self.minY = y
            self.maxZ = z
            self.minZ = z
        if x > self.maxX: self.maxX = x
        elif x < self.minX: self.minX = x
        if y > self.maxY: self.maxY = y
        elif y < self.minY: self.minY = y
        if z > self.maxZ: self.maxZ = z
        elif z < self.minZ: self.minZ = z

    def add_face(self, v1, v2, v3):
        f = Face(self.next_face_name, v1, v2, v3)
        self.next_face_name += 1
        self.faces.append(f)
        for vs, ve in [(v1, v2), (v2, v3), (v3, v1)]:
            if self.edges.has_key((vs, ve)):
                e = self.edges[(vs, ve)]
            elif self.edges.has_key((ve, vs)):
                e = self.edges[(ve, vs)]
            else:
                e = Edge(vs, ve)
                self.edges[(vs, ve)] = e
            e.add_face(f)
            f.add_edge(e)
        for v in [v1, v2, v3]:
            v.add_face(f)
  
    def allocate_volumes(self):
        to_grow = []
        for face in self.faces:
            if face.volume is None:
                face.volume = self.next_volume_name
                self.face_to_vol[face.name] = face.volume
                self.next_volume_name += 1
                self.volumes[face.volume]= [face]
                to_grow.append(face)
                while to_grow:
                    f = to_grow.pop()
                    for e in f.edges:
                        for new_face in e.faces:
                            if new_face.volume is None:
                                new_face.volume = face.volume
                                self.face_to_vol[new_face.name] = face.volume
                                self.volumes[face.volume].append(new_face)
                                to_grow.append(new_face)
        
        

class Vertex:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.edges = []
        self.faces = []

    def add_edge(self, edge):
        self.edges.append(edge)

    def add_face(self, face):
        self.faces.append(face)

    def __sub__(self, v):
        return Vector(self.x - v.x, self.y - v.y, self.z - v.z)

    def normal(self):
        n = sum([f.normal for f in self.faces], nullVector)
        return n.normalise()

    def adjacent_verticies(self):
        return [e.v1 for e in self.edges if e.v2 is self] + [e.v2 for e in self.edges if e.v1 is self]

class Vector:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z
    def cross(self, v):
        return Vector(self.y * v.z - self.z * v.y,
                      self.z * v.x - self.x * v.z,
                      self.x * v.y - self.y * v.x)
    def __add__(self, v):
        return Vector(self.x + v.x, self.y + v.y, self.z + v.z)

    def normalise(self):
        m = (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5
        return Vector(self.x/m, self.y/m, self.z/m)

nullVector = Vector(0, 0, 0)

class Face:
    def __init__(self, name, v1, v2, v3):
        self.name = name
        self.vertices = v1, v2, v3
        self.normal = (v1 - v2).cross(v1 - v3)
        self.volume = None
        self.edges = []
    def add_edge(self, edge):
        self.edges.append(edge)

class Edge:
    def __init__(self, v1, v2):
        self.v1, self.v2 = v1, v2
        self.faces = []
        v1.add_edge(self)
        v2.add_edge(self)

    def add_face(self, face):
        self.faces.append(face)
    
    #def normal(self):
    #    sum([f.normal for f in self.faces])
        
def makeMesh(ply):
    mesh = Mesh()
    for v in ply["vertex"]: 
        mesh.add_vertex(v['x'], v['y'], v['z'])
    for face in ply["face"]:
        mesh.add_face(*[mesh.vertices[i] for i in face['vertex_indices']])
    mesh.allocate_volumes()
    return mesh


