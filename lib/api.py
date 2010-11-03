import httplib
import xml.dom.minidom
import base64
import re

from lib.utils import parse_xml

class XMLGatewayInterface(object):
    def __init__(self, host, ssl=False, auth=False, debug=False, special_params={}):
        """ initalize API call session

        host: hostname (apigateway.tld)
        ssl: True/False
        auth: accept a tuple with (username,password)
        debug: True/False
        """
        self.doc = xml.dom.minidom.Document()
        self.api_host = host
        self.api_ssl = ssl
        self.api_auth = auth
        self.debug = debug
        self.parse_xml = parse_xml
        self.special_ssl = special_params

    def reset(self):
        """ Resets the current API session """
        self.doc = xml.dom.minidom.Document()

    def set(self, path, child=False, attribute=False):
        """ Accepts a forward slash seperated path of XML elements to traverse and create if non existent.
        Optional child and target node attributes can be set. If the `child` attribute is a tuple
        it will create X child nodes by reading each tuple as (name, text, 'attribute:value') where value
        and attributes are optional for each tuple.

        - path: forward slash seperated API element path as string (example: "Order/Authentication/Username")
        - child: tuple of child node data or string to create a text node
        - attribute: sets the target XML attributes (string format: "Key:Value")
        """
        xml_path = path.split('/')
        xml_doc = self.doc

        # traverse full XML element path string `path`
        for element_name in xml_path:
            # get existing XML element by `element_name`
            element = self.doc.getElementsByTagName(element_name)
            if element: element = element[0]

            # create element if non existing or target element
            if not element or element_name == xml_path[-1:][0]:
                element = self.doc.createElement(element_name)
                xml_doc.appendChild(element)

            xml_doc = element

        if child:
            # create child elements from an tuple with optional text node or attributes
            # format: ((name1, text, 'attribute:value'), (name2, text2))
            if isinstance(child, tuple):
                for obj in child:
                    child = self.doc.createElement(obj[0])
                    if len(obj) >= 2:
                        element = self.doc.createTextNode(str(obj[1]))
                        child.appendChild(element)
                    if len(obj) == 3:
                        a = obj[2].split(':')
                        child.setAttribute(a[0], a[1])
                    xml_doc.appendChild(child)
            # create a single text child node
            else:
                element = self.doc.createTextNode(str(child))
                xml_doc.appendChild(element)

        # target element attributes
        if attribute:
            #checking to see if we have a list of attributes
            if '|' in attribute:
                attributes = attribute.split('|')
            else:
                #if not just put this into a list so we have the same data type no matter what
                attributes = [attribute]

            # adding attributes for each item
            for attribute in attributes:
                attribute = attribute.split(':')
                xml_doc.setAttribute(attribute[0], attribute[1])

    def query(self, path, child=False, attribute=False):
        """ Helper for single command API calls - returns the result right away and handles session reset """
        self.reset()
        self.set(path, child, attribute)
        resp = self.post()
        self.reset()
        return resp


    def post(self, api_uri):
        """ Submits the API request as XML formated string via HTTP POST and parse gateway response.
        This needs to be run after adding some data via `set` or automatically via `query`
        """
        request_body = self.doc.toxml('utf-8')

        if self.debug:
            print 'Connecting to %s/%s' % (self.api_host, api_uri)

        if self.api_ssl:
            if self.special_ssl:
                kwargs = self.special_ssl
                api = httplib.HTTPSConnection(self.api_host, **kwargs)
            else:
                api = httplib.HTTPSConnection(self.api_host)
        else:
            api = httplib.HTTPConnection(self.api_host)

        api.connect()
        api.putrequest('POST', api_uri, skip_host=True)
        api.putheader('Host', self.api_host)
        api.putheader('Content-type', 'text/xml; charset="utf-8"')
        api.putheader("Content-length", str(len(request_body)))
        api.putheader('User-Agent', 'yourdomain.net')
        api.endheaders()
        api.send(request_body)

        resp = api.getresponse()
        resp_data = resp.read()

        # debug request 
        if self.debug:
            print '*** REQUEST:\n%s' % self.doc.toprettyxml()

        # parse API call response
        if not resp.status == 200:
            raise RequestError('Gateway returned %i status' % resp.status)
            #debugging
            if self.debug:
                print 'Full response text: %s' % resp_data

        # parse XML response and return as dict
        try:
            resp_dict = self.parse_xml(resp_data)
        except:
            try:
                resp_dict = self.parse_xml('<?xml version="1.0"?><response>%s</response>' % resp_data)
            except:
                raise RequestError('Could not parse XML into JSON')

        # optional debug output
        if self.debug:
            print '*** RESPONSE:\n%s' % resp_data

        return resp_dict

class RequestError(Exception):
    """ Errors during the API Request """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

class GatewayError(Exception):
    """ Errors returned from API Gateway """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)
