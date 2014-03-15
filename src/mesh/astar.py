'''
Astar algorithm.
'''

from __future__ import division

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
        
        
