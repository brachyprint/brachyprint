
'''
Functions to read and write PLY files.

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

def read_ply(inputfile):
    '''
    Create a mesh from a ply file.
    '''

    ply = _read_ply(inputfile)

    mesh = Mesh()
    for v in ply["vertex"]: 
        mesh.add_vertex(v['x'], v['y'], v['z'])
    for face in ply["face"]:
        mesh.add_face(*[mesh.vertices[i] for i in face['vertex_indices']])
    #mesh.allocate_volumes()
    return mesh
    

def _read_ply(inputfile):
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
                if file_format == ('binary_little_endian', '1.0'):
                    if propertyType == "float":
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
        f.write(r)


