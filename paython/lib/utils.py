import re
import calendar
import xml

from datetime import datetime
from suds.sax.text import Text as sudTypeText # for the 'parse_soap()' string type

from paython.exceptions import GatewayError

CARD_TYPES = {
    'visa': r'4\d{12}(\d{3})?$',
    'amex': r'37\d{13}$',
    'mc': r'5[1-5]\d{14}$',
    'discover': r'6011\d{12}',
    'diners': r'(30[0-5]\d{11}|(36|38)\d{12})$'
}

def parse_xml(element):
    """
    Parse an XML API Response xml.dom.minidom.Document. Returns the result as dict or string
    depending on amount of child elements. Returns None in case of empty elements
    """
    if not isinstance(element, xml.dom.minidom.Node):
        try:
            element = xml.dom.minidom.parseString(element)
        except xml.parsers.expat.ExpatError as e:
            raise GatewayError("Error parsing XML: {0}".format(e))

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

def is_valid_cc(cc):
    """
    Uses Luhn Algorithm for credit card number validation. http://en.wikipedia.org/wiki/Luhn_algorithm
    """
    try:
        num = map(int, cc)
    except ValueError:
        return False
    else:
        return not sum(num[::-2] + map(lambda d: sum(divmod(d * 2, 10)), num[-2::-2])) % 10

def is_valid_exp(month, year):
    """
    Uses datetime to compare string of card expiration to the time right now
    """
    month = int(month)
    year = int(year)

    exp_date_obj = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59, 59)
    return datetime.now() < exp_date_obj

def is_valid_cvv(cc_cvv):
    """
    Simple regex for card validator length & type.
    """
    return re.match(r'^[\d+]{3,4}$', cc_cvv)

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
    return "{0}/{1}".format(month, year)

def is_valid_email(email):
    """
    Based on "The Perfect E-Mail Regex" : http://fightingforalostcause.net/misc/2006/compare-email-regex.php
    """
    pat = '^([\w\!\#$\%\&\'\*\+\-\/\=\?\^\`{\|\}\~]+\.)*[\w\!\#$\%\&\'\*\+\-\/\=\?\^\`{\|\}\~]+@((((([a-z0-9]{1}[a-z0-9\-]{0,62}[a-z0-9]{1})|[a-z])\.)+[a-z]{2,6})|(\d{1,3}\.){3}\d{1,3}(\:\d{1,5})?)$'
    return re.search(pat, email, re.IGNORECASE)

def transform_keys():
    raise NotImplemented
