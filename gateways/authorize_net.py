import urllib

class Authorize(object):
    """TODO needs docstring"""
    API_BASE = {
        'transaction' : 'secure.authorize.net', # https
        'test' : 'test.authorize.net'
    }

    API_URI = {
        'transaction' : '/gateway/transact.dll'
    }

    REQUEST_DICT = {}
    VERSION = '3.1'
    TRANS_DATA_KEYS = ['x_first_name', 'x_last_name', 'x_zip', 'x_city', 'x_state', 
                         'x_email', 'x_customer_ip', 'x_card_code', 'x_exp_date', 'x_card_num']

    # response index keys to map the value to its proper dictionary key
    RESP_DICT_KEYS = {
        '1':'response_code',
        '3':'response_reason_code',
        '4':'response_reason_text',
        '5':'authorization_code',
        '6':'avs_response',
        '7':'transaction_id',
        '10':'amount',
        '12':'transaction_type',
        '13':'customer_id',
        '39':'card_code_response',
        '41':'last_four_of_card',
        '42':'card_type',
        '44':'request_amount',
    }

    debug = False

    def __init__(self, user='test', password='testpassword', debug=False):
        self.REQUEST_DICT['x_login'] = user
        self.REQUEST_DICT['x_tran_key'] = password
        
        if debug:
            self.debug = True

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
        self.REQUEST_DICT['x_amount'] = amount
        self.REQUEST_DICT['x_type'] = 'AUTH_ONLY'
        self.REQUEST_DICT['x_delim_data'] = 'TRUE'

        #updating from trans_data dictionary
        self.REQUEST_DICT.update(trans_data)

        # build our URL
        request_query = '?%s' % urllib.urlencode(self.REQUEST_DICT)

        # still building
        if self.debug:
            url = self.API_BASE['test']+self.API_URI['transaction'] # here just in case we want to granularly change endpoint
        else:
            url = self.API_BASE['transaction']+self.API_URI['transaction'] # here just in case we want to granularly change endpoint

        # make the request
        response_dict = self.get(url, request_query)

        return response_dict

    def settle(self, amount=None, trans_id=None):
        """
        Sends a transaction to settle takes amount to settle on trans_id :) We love this!
        """
        if not trans_id or not amount: return {'error':'no transaction id or amount'}

        self.REQUEST_DICT['x_type'] = 'PRIOR_AUTH_CAPTURE'
        self.REQUEST_DICT['x_delim_data'] = 'TRUE'
        self.REQUEST_DICT['x_trans_id'] = trans_id
        self.REQUEST_DICT['x_amount'] = amount
        
        # build our URL
        request_query = '?%s' % urllib.urlencode(self.REQUEST_DICT)

        # still building
        if self.debug:
            url = self.API_BASE['test']+self.API_URI['transaction'] # here just in case we want to granularly change endpoint
        else:
            url = self.API_BASE['transaction']+self.API_URI['transaction'] # here just in case we want to granularly change endpoint

        # make the request
        response_dict = self.get(url, request_query)

        return response_dict

    def void(self, amount=None, trans_id=None):
        """
        Send a transaction to be voided (in full)
        """
        if not trans_id: return {'error':'no transaction id'}

        self.REQUEST_DICT['x_type'] = 'VOID'
        self.REQUEST_DICT['x_delim_data'] = 'TRUE'
        self.REQUEST_DICT['x_trans_id'] = trans_id

        # build our URL
        request_query = '?%s' % urllib.urlencode(self.REQUEST_DICT)

        # still building
        if self.debug:
            url = self.API_BASE['test']+self.API_URI['transaction'] # here just in case we want to granularly change endpoint
        else:
            url = self.API_BASE['transaction']+self.API_URI['transaction'] # here just in case we want to granularly change endpoint

        # make the request
        response_dict = self.get(url, request_query)

        return response_dict

    def credit(self, amount=None, trans_id=None, card_num=None):
        """
        Send a transaction to be refunded (partially or fully)
        """
        #basic validation
        if not trans_id or not card_num: return {'error':'no transaction id or card number'}
        
        self.REQUEST_DICT['x_delim_data'] = 'TRUE'
        self.REQUEST_DICT['x_type'] = 'CREDIT'
        self.REQUEST_DICT['x_trans_id'] = trans_id
        self.REQUEST_DICT['x_card_num'] = card_num

        if amount: #check to see if we should send an amount
            self.REQUEST_DICT['x_amount'] = amount

        # build our URL
        request_query = '?%s' % urllib.urlencode(self.REQUEST_DICT)

        # still building
        if self.debug:
            url = self.API_BASE['test']+self.API_URI['transaction'] # here just in case we want to granularly change endpoint
        else:
            url = self.API_BASE['transaction']+self.API_URI['transaction'] # here just in case we want to granularly change endpoint

        # make the request
        response_dict = self.get(url, request_query)

        return response_dict

    def get(self, uri, params):
        """
        Sends any given request to authorize & returns dictionary of returned values
        """
        try:
            # make le request
            request = urllib.urlopen('https://%s%s' % (uri, params))
            response = ';%s' % request.read()

            response = response.split(';')

            new_response = {}
            i = 0
            # this is how we create the response dictionary
            for item in response:
                ikey = str(i)
                if ikey in self.RESP_DICT_KEYS:
                    new_response[self.RESP_DICT_KEYS[ikey]] = item
                i += 1

            response = new_response
            # returning the response!
            return response
        except:
            return {'error':'problem at gateway level'}

# REQUEST: 
# -----------
# x_type=AUTH_ONLY, CREDIT, PRIOR_AUTH_CAPTURE, VOID
# x_amount
# ***
# x_card_num=13, 16 or last 4 for CREDIT
# x_exp_date=MM-YY
# x_card_code
# ***
# x_trans_id
# x_split_tender_id
# x_auth_code
# x_delim_data
# x_delim_char=;
# x_first_name
# x_last_name
# x_zip
# x_city
# x_state
# x_email
# x_customer_ip

# RESPONSE:
# -------------
# 1) Response Code: 1 = Approved, 2 = Declined, 3 = Error, 4 = Held for Review
# 3) Response Reason Code
# 4) Response Reason Text
# 5) Authorization Code
# 6) AVS Response: A = Address (Street) matches, ZIP does not, P = AVS not applicable for this transaction, W = Nine digit ZIP matches, Address (Street) does not, X = Address (Street) and nine digit ZIP match, Y = Address (Street) and five digit ZIP match, Z = Five digit ZIP matches, Address (Street) does not
# 7) Transaction ID: 
# 10) Amount:
# 12) Transaction Type:
# 13) Customer ID: 
# 39) Card Code Response:
# 41) Last Four
# 42) Card Type:
# 44) Requested Amount:
