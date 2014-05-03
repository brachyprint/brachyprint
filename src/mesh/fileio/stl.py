
'''
Functions to read and write STL files.

See https://en.wikipedia.org/wiki/STL_%28file_format%29

read_stl(filename)
write_stl(mesh, filename)
'''

from mesh import *
import struct

STL_FORMAT_ASCII = 1
STL_FORMAT_BINARY = 2

class StlWriter(object):
    '''
    StlWriter

    Class to write STL files.
    '''

    def __init__(self, outputformat=STL_FORMAT_ASCII):
        self.outputformat = outputformat
    
    def write(self, m, name, filename):
        '''
        Write the file in the specified format.
        '''
        if self.outputformat == STL_FORMAT_ASCII:
            self.write_ascii(m, name, filename)
        elif self.outputformat == STL_FORMAT_BINARY:
            self.write_binary(m, name, filename)
        else:
            raise TypeError()

    def write_ascii(self, m, name, filename):
        with open(filename, 'wb') as fp:
            # write the header
            fp.write("solid %s\n" % (name))

            for f in m.faces:
                n = f.normal.normalise()
                v = f.vertices

                fp.write("facet normal %f %f %f\n" % (n[0], n[1], n[2]))
                fp.write("    outer loop\n")
                for i in range(3):
                    fp.write("        vertex %f %f %f\n" % (v[i][0], v[i][1], v[i][2]))
                fp.write("    endloop\n")
                fp.write("endfacet\n")

            # write the footer
            fp.write("endsolid %s\n" % (name))
    
    def write_binary(self, m, name, filename):
        with open(filename, 'wb') as fp:
            # write the header
            count = 0
            fp.write(struct.pack("80sI", b'Mesh binary STL writer', count))

            for f in m.faces:
                n = f.normal.normalise()
                v = f.vertices

                face = [   n[0],    n[1],    n[2],
                        v[0][0], v[0][1], v[0][2],
                        v[1][0], v[1][1], v[1][2],
                        v[2][0], v[2][1], v[2][2],
                        0 ]
                fp.write(struct.pack("12fH", *face))

                count = count + 1

            # overwrite the header with the number of faces output
            fp.seek(0)
            fp.write(struct.pack("80sI", b'Mesh Binary STL Writer', count))


class StlReader(object):
    '''
    StlReader

    Class to read STL files.
    '''

    def __init__(self):
        self.strict = False

    def read(self, m, filename):
        with open(filename, 'rb') as fp:

            fileContent = fp.read()

            if len(fileContent) < 5:
                raise IOError("Not enough data")

            # read the header
            if fileContent[0:4] == "80sI":
                self.decode_binary(m, fileContent)
            elif fileContent[0:5] == "solid":
                self.decode_ascii(m, fileContent.splitlines())
            else:
                raise IOError("Invalid STL file")

    def decode_ascii(self, m, lines):
        mode = 0
        vs = []
        all_vertices = {}
        solid_name = lines[0].strip().split(' ')[1]
        for i in range(1, len(lines)): # in lines:
            words = lines[i].strip().split(' ')
            if len(words) == 1 and words[0] == '':
                continue

            if mode == 0:
                if len(words) >= 2 and words[0] == "endsolid":
                    if words[1] != solid_name and self.strict:
                        raise IOError("Invalid STL file -- expecting 'endsolid %s' on line %i" % (solid_name, i))
                    return
                if len(words) < 2 or words[0] != "facet" or words[1] != "normal" :
                    raise IOError("Invalid STL file -- expecting 'facet normal' on line %i" % (i))
                else:
                    mode = 1
                    continue
            elif mode == 1:
                if len(words) < 2 or words[0] != "outer" or words[1] != "loop":
                    raise IOError("Invalid STL file -- expecting 'outer loop' on line %i" % (i))
                else:
                    mode = 2
                    continue
            elif mode == 2 or mode == 3 or mode == 4:
                if len(words) < 4 or words[0] != "vertex":
                    raise IOError("Invalid STL file -- expecting 'vertex' on line %i" % (i))
                v = Vector([float(w) for w in words[1:4]])
                vs.append(v)
                if mode == 4:
                    # check if the vertices already exist in the mesh
                    fv = []
                    for v in vs:
                        if v in all_vertices:
                            fv.append(all_vertices[v])
                        else:
                            p = m.add_vertex(v)
                            all_vertices[v] = p
                            fv.append(p)
                    # create face
                    m.add_face(fv)
                    vs = []
                mode += 1
            elif mode == 5:
                if len(words) < 1 or words[0] != "endloop":
                    raise IOError("Invalid STL file -- expecting 'endloop' on line %i" % (i))
                mode = 6
            elif mode == 6:
                if len(words) < 1 or words[0] != "endfacet":
                    raise IOError("Invalid STL file -- expecting 'endfacet' on line %i" % (i))
                mode = 0

        raise IOError("Invalid STL file -- unexpectedly reached end of file")


    def decode_binary(self, m, data):
        raise NotImplementedError()


def write_stl(m, filename, name="mesh", fileformat=STL_FORMAT_ASCII):
    '''
    Write a Mesh object to an STL file.

    Example:
        import mesh
        m = mesh.Mesh()
        mesh.primitives.add_cylinder(m, 10, 100, 10)
        mesh.fileio.write_stl(m, "cylinder.stl", fileformat=mesh.fileio.STL_FORMAT_BINARY)
    '''
    StlWriter(fileformat).write(m, name, filename)


def read_stl(m, filename):
    '''
    Read an STL file and add it to a Mesh object.

    Example:
        import mesh
        m = mesh.Mesh()
        mesh.fileio.read_stl(m, "cylinder.stl")
    '''
    return StlReader().read(m, filename)

