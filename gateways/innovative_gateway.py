import urllib
import urlparse

class InnovativeGW(object):

    API_BASE = {
        'transaction' : 'transactions.innovativegateway.com', # https
    }

    API_URI = {
        'transaction' : '/servlet/com.gateway.aai.Aai'
    }

    REQUEST_DICT = {}
    TRANS_DATA_KEYS = ['ccname', 'baddress', 'bcity', 'bstate', 'bzip', 'bphone',
                         'email', 'ccnumber', 'cardtype', 'ccidentifier1', 'month', 'year']

    debug = False

    def __init__(self, user='gatewaytest', password='GateTest2002', debug=False):
        self.REQUEST_DICT['username'] = user
        self.REQUEST_DICT['pw'] = password
        self.REQUEST_DICT['target_app'] = 'WebCharge_v5.06'
        self.REQUEST_DICT['response_mode'] = 'simple'
        self.REQUEST_DICT['response_fmt'] = 'url_encoded'
        self.REQUEST_DICT['upg_auth'] = 'zxcvlkjh'
        self.REQUEST_DICT['bcountry'] = 'US'
        self.REQUEST_DICT['baddress1'] = ''
        
        if debug:
            self.debug = True

    def sale(self, amount=None, trans_data=None):
        """
        Sends charge for sale capture based on amount
        """
        response_dict = {}

        # basic validation
        if not amount: response_dict['error'] = 'no amount specified'

        # basic validation
        if not all([trans_data.get(key) for key in self.TRANS_DATA_KEYS]): response_dict['error'] = 'missing transaction data'

        # return on error
        if 'error' in response_dict: return response_dict

        # other wise handle business
        self.REQUEST_DICT['fulltotal'] = amount
        self.REQUEST_DICT['trantype'] = 'sale'

        #updating from trans_data dictionary
        self.REQUEST_DICT.update(trans_data)

        # build our URL
        request_query = '%s' % urllib.urlencode(self.REQUEST_DICT)
        url = self.API_BASE['transaction']+self.API_URI['transaction'] # here just in case we want to granularly change endpoint

        # make the request
        response_dict = self.get(url, request_query)

        return response_dict

    def auth(self, amount=None, trans_data=None):
        """
        Sends charge for authorization based on amount
        """
        response_dict = {}

        # validation
        if not amount: response_dict['error'] = 'no amount specified'

        # validation
        if not all([trans_data.get(key) for key in self.TRANS_DATA_KEYS]): response_dict['error'] = 'missing transaction data'

        # return on error
        if 'error' in response_dict: return response_dict

        # other wise handle business
        self.REQUEST_DICT['fulltotal'] = amount
        self.REQUEST_DICT['trantype'] = 'preauth'

        #updating from trans_data dictionary
        self.REQUEST_DICT.update(trans_data)

        # build our URL
        request_query = '%s' % urllib.urlencode(self.REQUEST_DICT)
        url = self.API_BASE['transaction']+self.API_URI['transaction'] # here just in case we want to granularly change endpoint

        # make the request
        response_dict = self.get(url, request_query)

        return response_dict

    def settle(self, amount=None, trans_id=None, ref=None, card_data=None):
        """
        Sends a transaction to settle takes amount to settle on trans_id :) We love this!
        """
        if not trans_id or not amount: return {'error':'no transaction id or amount'}

        self.REQUEST_DICT['trantype'] = 'postauth'
        self.REQUEST_DICT['reference'] = ref
        self.REQUEST_DICT['trans_id'] = trans_id
        self.REQUEST_DICT['authamount'] = amount
        self.REQUEST_DICT['fulltotal'] = amount
        
        # build our URL
        request_query = '%s' % urllib.urlencode(self.REQUEST_DICT)

        # still building
        url = self.API_BASE['transaction']+self.API_URI['transaction'] # here just in case we want to granularly change endpoint

        # make the request
        response_dict = self.get(url, request_query)

        return response_dict

    def credit(self, amount=None, trans_id=None, ref=None, ordernumber=None):
        """
        Send a transaction to be refunded (partially or fully)
        """
        if not trans_id or not ref: return {'error':'no transaction id or ref number'}

        self.REQUEST_DICT['trantype'] = 'credit'
        self.REQUEST_DICT['reference'] = ref
        self.REQUEST_DICT['trans_id'] = trans_id
        self.REQUEST_DICT['ordernumber'] = ordernumber

        #check to see if we should send an amount
        if amount: 
            self.REQUEST_DICT['fulltotal'] = amount

        # build our URL
        request_query = '%s' % urllib.urlencode(self.REQUEST_DICT)

        # still building
        url = self.API_BASE['transaction']+self.API_URI['transaction'] # here just in case we want to granularly change endpoint

        # make the request
        response_dict = self.get(url, request_query)

        return response_dict

    def void(self, amount=None, trans_id=None, ref=None, ordernumber=None):
        """
        Send a transaction to either be voided (in full) or refunded (partially or fully)
        """
        if not trans_id or not ref: return {'error':'no transaction id or ref number'}

        self.REQUEST_DICT['trantype'] = 'void'
        self.REQUEST_DICT['reference'] = ref
        self.REQUEST_DICT['trans_id'] = trans_id
        self.REQUEST_DICT['ordernumber'] = ordernumber

        # build our URL
        request_query = '%s' % urllib.urlencode(self.REQUEST_DICT)

        # still building
        url = self.API_BASE['transaction']+self.API_URI['transaction'] # here just in case we want to granularly change endpoint

        # make the request
        response_dict = self.get(url, request_query)

        return response_dict

    def get(self, uri, params):
        """
        Sends any given request to authorize & returns dictionary of returned values
        """
        if self.debug:
            print '*******(request)**********\n', uri, params
        try:
            # make le request
            request = urllib.urlopen('https://%s' % (uri,),  params) 
            response = '%s' % request.read()

            if self.debug:
                print '******************REQUEST***********', 'https://%s%s' % (uri, params)
                print '*************RESPONSE*****************', response

            new_response = urlparse.parse_qsl(response)

            response = dict(new_response)
            
            # returning the response!
            return response
        except:
            return {'error':'problem at gateway level'}

# 6) AVS Response: X = Both the zip code (the AVS 9-digit) and the street address match. Y = Both the zip (the AVS 5-digit) and the street address match.  A = The street address matches, but the zip code does not match. W = The 9-digit zip codes matches, but the street address does not match. Z= The 5-digit zip codes matches, but the street address does not match. N = Neither the street address nor the postal code matches. R = Retry, System unavailable (maybe due to timeout). S = Service not supported. U = Address information unavailable. E = Data not available/error invalid. G = Non-US card issuer that does not participate in AVS