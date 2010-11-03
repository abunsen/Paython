import xml.dom.minidom

def parse_xml(element):
    """
    Parse an XML API Response xml.dom.minidom.Document. Returns the result as dict or string
    depending on amount of child elements. Returns None in case of empty elements
    """
    if not isinstance(element, xml.dom.minidom.Node):
        try:
            element = xml.dom.minidom.parseString(element)
        except: raise

    # return DOM element with single text element as string
    if len(element.childNodes) == 1:
        child = element.childNodes[0]
        if child.nodeName == '#text':
            return child.nodeValue.strip()

    # parse the child elements and return as dict
    root = {}

    for e in element.childNodes:
        t = {}

        if e.nodeName == '#text':
            if not e.nodeValue.strip(): continue

        if e.attributes:
            t['attribute'] = {}
            for attribute in e.attributes.values():
                t['attribute'][attribute.nodeName] = attribute.childNodes[0].nodeValue

        if e.childNodes:
            if t.has_key('attribute'):
                t['meta'] = parse_xml(e)
            else:
                if len(e.childNodes) == 1:
                    if e.firstChild.nodeType == xml.dom.Node.CDATA_SECTION_NODE:
                        t = e.firstChild.wholeText
                    else:
                        t = parse_xml(e)
                else:
                    t = parse_xml(e)

        if not t:
            t = e.nodeValue

        if root.has_key(e.nodeName):
            if not isinstance(root[e.nodeName], list):
                tmp = []
                tmp.append(root[e.nodeName])
            tmp.append(t)
            t = tmp

        root[e.nodeName] = t

    return root