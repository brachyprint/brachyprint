import parseply
import struct
from routes import *
from heapq import heappush, heappop

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
        

class Mesh(object):
    '''
    Class representing a mesh.
    '''

    def __init__(self):
        self.vertices = []
        self.faces = []
        self.edges = {}
        self.maxX, self.minX = None, None
        self.maxY, self.minY = None, None
        self.maxZ, self.minZ = None, None
        #self.volumes = {}
        self.next_vertex_name = 0
        self.next_face_name = 0
        self.next_volume_name = 0
        self.face_to_vol = {}

    def add_vertex(self, x, y, z):
        v = Vertex(x,y,z, self.next_vertex_name)
        self.next_vertex_name += 1
        self.vertices.append(v)
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
        return v

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

    def get_path(self, s1, s2):
        s2Postion = s2[0], s2[1], s2[2]
        s2Face = self.faces[s2[3]]
        priority_queue = []
        visited = {}
        if s1[3] == s2[3]:
            return [point_to_point(s1, s2)]
        for v in self.faces[s1[3]].vertices:
            pv = point_to_vertex(s1[0], s1[1], s1[2], v, s2Postion, s2Face)
            heappush(priority_queue, (pv.dist() + pv.crowdist(), pv.dist(), [pv]))	
        while (len(priority_queue) > 0):
            dist_plus_crow, dist, paths = heappop(priority_queue)
            lastPath = paths[-1]
            end = lastPath.end()
            if end not in visited:
                if lastPath.finished():
                    #Finished!
                    return paths
                else:
                    visited[end] = True
                    for newPath in lastPath.new_Paths():
                        new_dist = newPath.dist()
                        heappush(priority_queue, (dist + new_dist + pv.crowdist(), dist + new_dist, paths + [newPath]))

    def cloneSubVol(self, triangle, avoidEdges):
        vertex_map = {}
        faces_copied = []
        to_grow = [triangle]
        newMesh = Mesh()
        i = 0
        while to_grow:
            i = i +1
            f = to_grow.pop()
            for v in f.vertices:
                if not vertex_map.has_key(v):
                    vertex_map[v] = newMesh.add_vertex(v.x, v.y, v.z)
            newMesh.add_face(*[vertex_map[v] for v in f.vertices])
            faces_copied.append(f)
            for e in f.edges:
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
  
#    def allocate_volumes(self):
#        '''Allocate each face to a particular volume.
#
#        '''
#        to_grow = []
#        for face in self.faces:
#            if face.volume is None:
#                face.volume = self.next_volume_name
#                self.face_to_vol[face.name] = face.volume
#                self.next_volume_name += 1
#                self.volumes[face.volume]= [face]
#                to_grow.append(face)
#                while to_grow:
#                    f = to_grow.pop()
#                    for e in f.edges:
#                        for new_face in e.faces:
#                            if new_face.volume is None:
#                                new_face.volume = face.volume
#                                self.face_to_vol[new_face.name] = face.volume
#                                self.volumes[face.volume].append(new_face)
#                                to_grow.append(new_face)
#        
        
class Vector(object):
    '''
    Class representing a vector.
    '''

    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def __eq__(self, v):
        if isinstance(v, Vector):
            return self.x == v.x and self.y == v.y and self.z == v.z
        elif isinstance(v, list):
            return self.x == v[0] and self.y == v[1] and self.z == v[2]
        else:
            raise NotImplementedError

    def __gt__(self, v):
        raise TypeError("Ambiguous meaning for a Vector")

    def __lt__(self, v):
        raise TypeError("Ambiguous meaning for a Vector")

    def __lshift__(self, other):
        raise TypeError("Vector is not a binary type")

    def __rshift__(self, other):
        raise TypeError("Vector is not a binary type")

    def __and__(self, other):
        raise TypeError("Vector is not a binary type")

    def __xor__(self, other):
        raise TypeError("Vector is not a binary type")

    def __or__(self, other):
        raise TypeError("Vector is not a binary type")

    def __add__(self, v):
        if isinstance(v, Vector):
            return Vector(self.x + v.x, self.y + v.y, self.z + v.z)
        else:
            raise NotImplementedError

    def __sub__(self, v):
        if isinstance(v, Vector):
            return Vector(self.x - v.x, self.y - v.y, self.z - v.z)
        else:
            raise NotImplementedError

    def __mul__(self, val):
        if isinstance(val, float) or isinstance(val, int):
            return Vector(self.x*val, self.y*val, self.z*val)
        else:
            raise NotImplementedError

    def __rmul__(self, other):
        self.__mul__(other)

    def __div__(self, val):
        if isinstance(val, float) or isinstance(val, int):
            return Vector(self.x/val, self.y/val, self.z/val)
        else:
            raise NotImplementedError

    def __rdiv__(self, other):
        self.__div__(other)

    def __truediv__(self, val):
        if isinstance(val, float) or isinstance(val, int):
            return Vector(self.x/val, self.y/val, self.z/val)
        else:
            raise NotImplementedError

    def __rtruediv__(self, other):
        self.__truediv__(other)

    def __iadd__(self, v):
        if isinstance(v, Vector):
            self.x += v.x
            self.y += v.y
            self.z += v.z
            return self
        else:
            raise NotImplementedError
        
    def __isub__(self, v):
        if isinstance(v, Vector):
            self.x -= v.x
            self.y -= v.y
            self.z -= v.z
            return self
        else:
            raise NotImplementedError

    def __imul__(self, val):
        if isinstance(val, float) or isinstance(val, int):
            self.x *= val
            self.y *= val
            self.z *= val
            return self
        else:
            raise NotImplementedError

    def __getitem__(self, i):
        if i == 0:
            return self.x
        elif i == 1:
            return self.y
        elif i == 2:
            return self.z
        else:
            raise IndexError

    def __len__(self):
        return 3

    def __repr__(self):
        return "<Vector x:%f y:%f z:%f>" % (self.x, self.y, self.z)

    def __str__(self):
        return "From str method of Vector: x is %f, y is %f, z is %f" % (self.x, self.y, self.z)

    def cross(self, v):
        return Vector(self.y * v.z - self.z * v.y,
                      self.z * v.x - self.x * v.z,
                      self.x * v.y - self.y * v.x)

    def normalise(self):
        m = (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5
        if m == 0.0:
            return Vector(self.x, self.y, self.z)
        else:
            return Vector(self.x/m, self.y/m, self.z/m)


nullVector = Vector(0, 0, 0)


class Vertex(Vector):
    '''
    A class representing a mesh vertex.
    '''

    def __init__(self, x, y, z, name):
        self.x, self.y, self.z = x, y, z
        self.name = name
        self.edges = []
        self.faces = []

    def __repr__(self):
        return "<Vertex x:%f y:%f z:%f name:%d>" % (self.x, self.y, self.z, self.name)

    def __str__(self):
        return "From str method of Vertex: x is %f, y is %f, z is %f, name is %d" % (self.x, self.y, self.z, self.name)

    def add_edge(self, edge):
        '''
        Associate an edge with the vertex.
        '''
        self.edges.append(edge)

    def add_face(self, face):
        '''
        Associate a face with the vertex.
        '''
        self.faces.append(face)

    def tovector(self):
        return Vector(self.x, self.y, self.z)

    def normal(self):
        '''
        Determine a normal at the vertex by averaging its associated face normals.
        '''
        n = sum([f.normal for f in self.faces], nullVector)
        return n.normalise()

    def adjacent_vertices(self):
        '''
        Return (vertex, edge) for all adjacent vertices.
        '''
        return [(e.v1, e) for e in self.edges if e.v2 is self] + [(e.v2, e) for e in self.edges if e.v1 is self]


class Face:
    '''
    A class representing a mesh face.
    '''

    def __init__(self, name, v1, v2, v3):
        self.name = name
        self.vertices = v1, v2, v3
        self.normal = (v1 - v2).cross(v1 - v3)
        self.volume = None
        self.edges = []

    def add_edge(self, edge):
        self.edges.append(edge)


class Edge:
    '''
    A class representing a mesh edge.
    '''

    def __init__(self, v1, v2):
        self.v1, self.v2 = v1, v2
        self.faces = []
        v1.add_edge(self)
        v2.add_edge(self)

    def add_face(self, face):
        self.faces.append(face)
    
        
def makeMesh(ply):
    mesh = Mesh()
    for v in ply["vertex"]: 
        mesh.add_vertex(v['x'], v['y'], v['z'])
    for face in ply["face"]:
        mesh.add_face(*[mesh.vertices[i] for i in face['vertex_indices']])
    #mesh.allocate_volumes()
    return mesh


