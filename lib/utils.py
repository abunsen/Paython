import re
import calendar
import xml.dom.minidom

from datetime import datetime

# for the 'parse_soap()' string type
from suds.sax.text import Text as sudTypeText

CARD_TYPES = {
    'visa' : '4\d{12}(\d{3})?$',
    'amex' : '37\d{13}$',
    'mc' : '5[1-5]\d{14}$',
    'discover':'6011\d{12}',
    'diners':'(30[0-5]\d{11}|(36|38)\d{12})$'
}

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

def parse_soap():
    """
    Parse a suds response. Returns the result as a dict.
    """
    if isinstance(obj, dict):
        for k in obj.keys():
            obj[k] = to_dict(obj[k], classkey)

        return obj
    elif hasattr(obj, "__dict__"):
        data = dict([(key, parse_soap(value, classkey)) for key, value in obj.__dict__.iteritems() if not callable(value) and not key.startswith('_')])
        
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__

        return data
    elif hasattr(obj, "__iter__"):
        return [parse_soap(v, classkey) for v in obj]
    else:
        if isinstance(obj, sudTypeText):
            obj = str(obj)
        
        return obj

def is_valid_cc(cc):
    """
    Uses Luhn Algorithm for credit card number validation. http://en.wikipedia.org/wiki/Luhn_algorithm
    """
    num = map(int, cc)
    return not sum(num[::-2] + map(lambda d: sum(divmod(d * 2, 10)), num[-2::-2])) % 10

def is_valid_exp(month, year):
    """
    Uses datetime to compare string of card expiration to the time right now
    """
    exp_date_obj = datetime(int(year), int(month), calendar.monthrange(year, month)[1], 23, 59, 59, 59)
    return datetime.now() > exp_date_obj

def check_cvv(cc_cvv):
    """
    Simple regex for card validator length & type.
    """
    if not re.match(r'^[\d+]{3,4}$', cc_cvv):
        return False 
    return True

def get_card_type(cc):
    """
    Gets card type by using card number
    """
    for k, v in CARD_TYPES.items():
        if re.match(v, cc):
            return k

def get_card_exp(month, year):
    """
    Gets the expiration date by concatenating strings
    """
    return '%s/%s' % (month, year)

def transform_keys():
    raise NotImplemented