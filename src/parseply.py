import re, struct

reStartHeader = re.compile("^ply$")
reFormat = re.compile("^format\s+(\S+)\s+(\S+)\s*$")
reComment = re.compile("^comment\s+")
reElement = re.compile("^element\s+(\S+)\s+(\d+)$")
reProperty = re.compile("^property\s+(.+)\s+(\S+)$")
reEndHeader = re.compile("^end_header$")

def parseply(inputfile):
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


