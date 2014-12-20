#    Brachyprint -- 3D printing brachytherapy moulds
#    Copyright (C) 2013-14  James Cranch, Martin Green and Oliver Madge
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

'''
Functions to read and write PLY files.

See https://en.wikipedia.org/wiki/PLY_%28file_format%29

read_ply(filename)
write_ply(mesh, filename)
'''

import re, struct
from mesh import *

reStartHeader = re.compile("^ply$")
reFormat = re.compile("^format\s+(\S+)\s+(\S+)\s*$")
reComment = re.compile("^comment\s+")
reElement = re.compile("^element\s+(\S+)\s+(\d+)$")
reProperty = re.compile("^property\s+(.+)\s+(\S+)$")
reEndHeader = re.compile("^end_header$")

class PlyReader(object):
    '''
    PlyReader

    Class to read PLY files.

    Example:
        import mesh
        m = mesh.Mesh()
        reader = mesh.fileio.PlyReader()
        for i in reader.read_part(m, filename):
            pass
    '''

    def __init__(self):
        pass

    def read(self, m, filename):
        for i in self.read_part(m, filename):
            pass

    def read_part(self, m, filename):
        """Read a ply file in parts.
        """

        with open(filename) as fp:
            ply = self._read_ply(fp)

        l = len(ply["vertex"])

        def chunk(l, n):
            """Yield n successive chunks from l.
            """
            newn = int(len(l) / n)
            for i in xrange(0, n-1):
                yield l[i*newn:i*newn+newn]
            yield l[n*newn-newn:]

        # Estimate the time split between vertex and face creation, with
        # 5 time steps in each part.

        v_ranges = chunk(ply["vertex"], 5)

        i = 0
        for vs in v_ranges:
            for v in vs:
                m.add_vertex(v['x'], v['y'], v['z'])
            yield i
            i += 1

        f_ranges = chunk(ply["face"], 5)
        for fs in f_ranges:
            for face in fs:
                m.add_face(*[m.vertices[index] for index in face['vertex']])
            yield i
            i += 1

    def _read_ply(self, inputfile):
        first_line = inputfile.readline()
        assert reStartHeader.match(first_line), "File does not begin with the string 'ply'"
        secound_line = inputfile.readline()
        formatMatch = reFormat.match(secound_line)
        assert formatMatch, "2nd line does not specify format."
        file_format = (formatMatch.group(1), formatMatch.group(2))
        assert file_format in [('binary_little_endian', '1.0')], "Format not supported"
        header = []
        line = inputfile.readline()
        while True:
            reElementMatch = reElement.match(line)
            if reElementMatch:
                elementName, elementCount = reElementMatch.group(1), int(reElementMatch.group(2))
                properties = []
                while True:
                    line = inputfile.readline()
                    rePropertyMatch = reProperty.match(line)
                    if rePropertyMatch: 
                        type_, name = rePropertyMatch.group(1), rePropertyMatch.group(2)
                        properties.append((type_, name))
                    elif reComment.match(line): pass
                    else: break
                header.append((elementName, elementCount, properties))
                continue
            if reEndHeader.match(line): break
            elif reComment.match(line): pass
            else: assert False, "Header format not recognised: %s" % line
            line = inputfile.readline()
        result = {}
        for elementName, elementCount, properties in header:
            items = []
            for n in range(elementCount):
                element = {}
                for propertyType, propertyName in properties:
                    # XXX: these seem to be synonyms?
                    propertyName = re.sub("_index$", "", propertyName)
                    propertyName = re.sub("_indices$", "", propertyName)
                    if file_format == ('binary_little_endian', '1.0'):
                        if propertyType == "float" or propertyType == "float32":
                            element[propertyName] = struct.unpack("<f", inputfile.read(4))[0]
                        elif propertyType == "list uchar int":
                            l = []
                            for m in range(struct.unpack("<B", inputfile.read(1))[0]):
                                l.append(struct.unpack("<i", inputfile.read(4))[0])
                            element[propertyName] = l
                        else:
                            assert False, "Property Type unknown: %s" % propertyType
                items.append(element)
            result[elementName] = items
        assert inputfile.read() == "", "Finished reading data however the file contains more information!"
        return result


def write_ply(m, filename):
    '''
    Write to a ply file.
    '''

    # construct output string
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
""" % (len(m.vertices), len(m.faces))
    for v in m.vertices:
        r = r + struct.pack("<f", v.x) + struct.pack("<f", v.y) + struct.pack("<f", v.z)
    for f in m.faces:
        r = r + struct.pack("<B", 3)
        for v in f.vertices:
            r = r + struct.pack("<i", m.vertices.index(v))

    # open the file and write out the ply string
    with open(filename, "w") as fp:
        fp.write(r)


def read_ply(m, filename):
    '''
    Read a PLY file and add it to a Mesh object.

    Example:
        import mesh
        m = mesh.Mesh()
        mesh.fileio.read_ply(m, "cylinder.ply")
    '''
    return PlyReader().read(m, filename)

