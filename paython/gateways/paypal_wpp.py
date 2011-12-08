import time

from paython.exceptions import MissingDataError
from paython.lib.api import GetGateway

class PaypalWPP(GetGateway):
    """TODO needs docstring"""
    DELIMITER = '&'
    VERSION = '54.0'

    # This is how we determine whether or not we allow 'test' as an init param
    API_URI = {
        'live': 'https://api-3t.paypal.com/nvp',
        'test': 'https://api-3t.sandbox.paypal.com/nvp'
    }

    # This is how we translate the common Paython fields to Gateway specific fields
    REQUEST_FIELDS = {
        #contact
        'full_name': None,
        'first_name': 'firstname',
        'last_name': 'lastname',
        'email': 'email',
        'phone': 'shiptophonenum',
        #billing
        'address': 'street',
        'address2': 'street2',
        'city': 'city',
        'state': 'state', 
        'zipcode': 'zip',
        'country': 'countrycode',
        'ip': 'ipaddress',
        #card
        'number': 'acct',
        'exp_date': 'expdate',
        'exp_month': None,
        'exp_year': None,
        'verification_value': 'cvv2',
        'card_type': 'creditcardtype',
        #shipping
        'ship_full_name': None,
        'ship_first_name': None,
        'ship_last_name': None,
        'ship_to_co': None,
        'ship_address': None,
        'ship_address2': None,
        'ship_city': None,
        'ship_state': None,
        'ship_zipcode': None,
        'ship_country': None,
        #transaction
        'amount': 'amt',
        'trans_type': 'method',
        'trans_id': 'transactionid',
        'alt_trans_id': 'authorizationid',
    }

    # Response Code: 1 = Approved, 2 = Declined, 3 = Error, 4 = Held for Review
    # AVS Responses: A = Address (Street) matches, ZIP does not,  P = AVS not applicable for this transaction,
    # AVS Responses (cont'd): W = Nine digit ZIP matches, Address (Street) does not, X = Address (Street) and nine digit ZIP match, 
    # AVS Responses (cont'd): Y = Address (Street) and five digit ZIP match, Z = Five digit ZIP matches, Address (Street) does not
    # response index keys to map the value to its proper dictionary key
    RESPONSE_KEYS = {
        'ack': 'response_code',
        'l_errorcode0': 'response_reason_code',
        'l_longmessage0': 'response_text',
        'correlationid': 'auth_code',
        #'correlationid':'alt_trans_id',
        'avscode': 'avs_response', 
        'transactionid': 'trans_id',
        'amt': 'amount',
        'cvv2match':'cvv_response',
    }

    # Map cc.py card types to paypal card types
    CARD_TYPES = {
        'visa': 'Visa',
        'amex': 'Amex',
        'mc': 'MasterCard',
        'discover': 'Discover',
    }

    debug = False
    test = False

    def __init__(self, username='test', password='testpassword', signature='', debug=False, test=False, delim=None):
        """
        setting up object so we can run 4 different ways (live, debug, test & debug+test)
        """
        self.set('USER', username)
        self.set('PWD', password)
        self.set('SIGNATURE', signature)
        self.set('VERSION', self.VERSION)

        # passing fields to bubble up to Base Class
        super(PaypalWPP, self).__init__(translations=self.REQUEST_FIELDS, debug=debug)

        if debug:
            self.debug = True

        if test:
            self.test = True
            if self.debug: 
                debug_string = " paython.gateways.paypal_wpp.__init__() -- You're in test mode (& debug, obviously) "
                print debug_string.center(80, '=')

        if delim:
            self.DELIMITER = delim

    def charge_setup(self):
        """
        standard setup, used for charges
        """
        #self.set('x_delim_data', 'TRUE')
        #self.set('x_delim_char', self.DELIMITER)
        #self.set('x_version', self.VERSION)
        if self.debug: 
            debug_string = " paython.gateways.paypal_wpp.charge_setup() Just set up for a charge "
            print debug_string.center(80, '=')

    def use_credit_card(self, credit_card):
        """
        Set up credit card info use (if necessary for transaction)
        """
        if hasattr(credit_card, '_exp_yr_style'): # here for gateways that like 2 digit expiration years
            credit_card.exp_year = credit_card.exp_year[-2:]

        for key, value in credit_card.__dict__.items():
            if not key.startswith('_'):
                try:
                    if self.REQUEST_FIELDS[key]:
                        if key == 'card_type':
                            value = self.CARD_TYPES[value]
                        elif key == 'exp_date':
                            value = value.replace('/', '')
                        self.set(self.REQUEST_FIELDS[key], value)
                except KeyError:
                    pass # it is okay to fail (on exp_month & exp_year)

    def auth(self, amount, credit_card=None, billing_info=None, shipping_info=None):
        """
        Sends charge for authorization based on amount
        """
        #set up transaction
        self.charge_setup() # considering turning this into a decorator?

        #setting transaction data
        self.set(self.REQUEST_FIELDS['amount'], amount)
        self.set(self.REQUEST_FIELDS['trans_type'], 'DoDirectPayment')
        self.set('paymentaction', 'Authorization')

        # validating or building up request
        if not credit_card:
            if self.debug: 
                debug_string = "paython.gateways.paypal_wpp.auth()  -- No CreditCard object present. You passed in %s " % (credit_card)
                print debug_string
            raise MissingDataError('You did not pass a CreditCard object into the auth method')
        else:
            self.use_credit_card(credit_card)

        if billing_info:
            self.set_billing_info(**billing_info)

        if shipping_info:
            self.set_shipping_info(**shipping_info)

        # send transaction to gateway!
        response, response_time = self.request()
        parsed_response = self.parse(response, response_time)
        parsed_response['trans_type'] = 'DoDirectPayment-Authorization'
        return parsed_response

    def settle(self, amount, trans_id):
        """
        Sends prior authorization to be settled based on amount & trans_id PRIOR_AUTH_CAPTURE
        """
        #set up transaction
        self.charge_setup() # considering turning this into a decorator?

        #setting transaction data
        self.set(self.REQUEST_FIELDS['trans_type'], 'DoCapture')
        self.set(self.REQUEST_FIELDS['amount'], amount)
        self.set(self.REQUEST_FIELDS['alt_trans_id'], trans_id)
        self.set('completetype', 'Complete')

        # send transaction to gateway!
        response, response_time = self.request()
        parsed_response = self.parse(response, response_time)
        parsed_response['trans_type'] = 'DoCapture'
        return parsed_response

    def capture(self, amount, credit_card=None, billing_info=None, shipping_info=None):
        """
        Sends transaction for capture (same day settlement) based on amount.
        """
        #set up transaction
        self.charge_setup() # considering turning this into a decorator?

        #setting transaction data
        self.set(self.REQUEST_FIELDS['amount'], amount)
        self.set(self.REQUEST_FIELDS['trans_type'], 'DoDirectPayment')
        self.set('paymentaction', 'Sale')

        # validating or building up request
        if not credit_card:
            if self.debug: 
                debug_string = "paython.gateways.paypal_wpp.capture()  -- No CreditCard object present. You passed in %s " % (credit_card)
                print debug_string
            raise MissingDataError('You did not pass a CreditCard object into the capture method')
        else:
            self.use_credit_card(credit_card)

        if billing_info:
            self.set_billing_info(**billing_info)

        if shipping_info:
            self.set_shipping_info(**shipping_info)

        # send transaction to gateway!
        response, response_time = self.request()
        parsed_response = self.parse(response, response_time)
        parsed_response['trans_type'] = 'DoDirectPayment-Sale'
        return parsed_response

    def void(self, trans_id):
        """
        Sends a transaction to be voided (in full)
        """
        #set up transaction
        self.charge_setup() # considering turning this into a decorator?

        #setting transaction data
        self.set(self.REQUEST_FIELDS['trans_type'], 'DoVoid')
        self.set(self.REQUEST_FIELDS['alt_trans_id'], trans_id)

        # send transaction to gateway!
        response, response_time = self.request()
        parsed_response = self.parse(response, response_time)
        parsed_response['trans_type'] = 'DoVoid'
        return parsed_response


    def credit(self, amount, trans_id, credit_card):
        """
        Sends a transaction to be refunded (partially or fully)
        Amount should be None for full refund
        """
        #set up transaction
        self.charge_setup() # considering turning this into a decorator?

        #setting transaction data
        self.set(self.REQUEST_FIELDS['trans_type'], 'RefundTransaction')
        self.set(self.REQUEST_FIELDS['trans_id'], trans_id)
        if amount: #check to see if we should send an amount
            self.set('refundtype', 'Partial')
            self.set(self.REQUEST_FIELDS['amount'], amount)
        else:
            self.set('refundtype', 'Full')

        # send transaction to gateway!
        response, response_time = self.request()
        parsed_response = self.parse(response, response_time)
        parsed_response['trans_type'] = 'RefundTransaction'
        return parsed_response

    def request(self):
        """
        Makes a request using lib.api.GetGateway.make_request() & move some debugging away from other methods.
        """
        # decide which url to use (test|live)
        if self.test:
            url = self.API_URI['test'] # here just in case we want to granularly change endpoint
        else:
            url = self.API_URI['live'] 

        if self.debug:  # I wish I could hide debugging
            debug_string = " paython.gateways.paypal_wpp.request() -- Attempting request to: "
            print debug_string.center(80, '=')
            debug_string = "\n %s with params: %s" % (url, self.query_string())
            print debug_string

        # make the request
        start = time.time() # timing it
        response = self.make_request(url)
        end = time.time() # done timing it
        response_time = '%0.2f' % (end-start)

        if self.debug: # debugging makes code look so nasty
            debug_string = " paython.gateways.paypal_wpp.request()  -- Request completed in %ss " % response_time
            print debug_string.center(80, '=')

        return response, response_time

    def parse(self, response, response_time):
        """
        On Specific Gateway due differences in response from gateway
        """
        import urllib
        if self.debug: # debugging is so gross
            debug_string = " paython.gateways.paypal_wpp.parse() -- Raw response: "
            print debug_string.center(80, '=')
            debug_string = "\n %s" % response
            print debug_string

        #splitting up response into a list so we can map it to Paython generic response
        response_tokens = {}
        for kv in response.split(self.DELIMITER):
            key, value = kv.split("=")
            response_tokens[key.lower()] = urllib.unquote(value)
        #assert False, response_tokens
        approved = response_tokens['ack'] == 'Success'

        if self.debug: # :& gonna puke
            debug_string = " paython.gateways.paypal_wpp.parse() -- Response as list: " 
            print debug_string.center(80, '=')
            debug_string = '\n%s' % response
            print debug_string

        return self.standardize(response, self.RESPONSE_KEYS, response_time, approved)
