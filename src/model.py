import parseply
import struct

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
        #self.volumes = {}
        self.next_face_name = 0
        self.next_volume_name = 0
        self.face_to_vol = {}

    def add_vertex(self, x, y, z):
        new_vertex = Vertex(x, y, z)
        self.vertices.append(new_vertex)
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
        return new_vertex

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
  
    #def allocate_volumes(self):
    #    to_grow = []
    #    for face in self.faces:
    #        if face.volume is None:
    #            face.volume = self.next_volume_name
    #            self.face_to_vol[face.name] = face.volume
    #            self.next_volume_name += 1
    #            self.volumes[face.volume]= [face]
    #            to_grow.append(face)
    #            while to_grow:
    #                f = to_grow.pop()
    #                for e in f.edges:
    #                    for new_face in e.faces:
    #                        if new_face.volume is None:
    #                            new_face.volume = face.volume
    #                            self.face_to_vol[new_face.name] = face.volume
    #                            self.volumes[face.volume].append(new_face)
    #                            to_grow.append(new_face)
        
    def cloneSubVol(self, triangle, avoidEdges):
        #print triangle
        #print avoidEdges
        vertex_map = {}
        faces_copied = []
        to_grow = [triangle]
        newMesh = Mesh()
        i = 0
        while to_grow:
            i = i +1
            #if i % 20 == 0:
                #print len(to_grow), len(faces_copied)
            f = to_grow.pop()
            for v in f.vertices:
                if not vertex_map.has_key(v):
                    vertex_map[v] = newMesh.add_vertex(v.x, v.y, v.z)
            newMesh.add_face(*[vertex_map[v] for v in f.vertices])
            faces_copied.append(f)
            for e in f.edges:
                #print e, avoidEdges[0]
                #if e in avoidEdges:
                    #print "Avoid"
                if e not in avoidEdges:
                    for neighbouring_face in e.faces:
                        if neighbouring_face not in faces_copied:
                            to_grow.append(neighbouring_face)
        #newMesh.allocate_volumes()
        return newMesh

    def save_ply(self):
        r = """ply
format binary_little_endian 1.0
comment Rough Cut
element vertex %i
property float x
property float y
property float z
element face %i
property list uchar int vertex_indices
end_header
""" % (len(self.vertices), len(self.faces))
        for v in self.vertices:
            r = r + struct.pack("<f", v.x) + struct.pack("<f", v.y) + struct.pack("<f", v.z)
        for f in self.faces:
            r = r + struct.pack("<B", 3)
            for v in f.vertices:
                r = r + struct.pack("<i", self.vertices.index(v))
        return r

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
        return [(e.v1, e) for e in self.edges if e.v2 is self] + [(e.v2, e) for e in self.edges if e.v1 is self]

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
    #mesh.allocate_volumes()
    return mesh


