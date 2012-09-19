import time

from paython.exceptions import MissingDataError
from paython.lib.api import GetGateway

class AuthorizeNet(GetGateway):
    """TODO needs docstring"""
    VERSION = '3.1'
    DELIMITER = ';'

    # This is how we determine whether or not we allow 'test' as an init param
    API_URI = {
        'live' : 'https://secure.authorize.net/gateway/transact.dll',
        'test' : 'https://test.authorize.net/gateway/transact.dll'
    }

    # This is how we translate the common Paython fields to Gateway specific fields
    REQUEST_FIELDS = {
        #contact
        'full_name' : None,
        'first_name': 'x_first_name',
        'last_name': 'x_last_name',
        'email': 'x_email',
        'phone': 'x_phone',
        #billing
        'address': 'x_address',
        'address2': None,
        'city': 'x_city',
        'state': 'x_state', 
        'zipcode': 'x_zip',
        'country': 'x_country',
        'ip': 'x_customer_ip',
        #card
        'number': 'x_card_num',
        'exp_date': 'x_exp_date',
        'exp_month': None,
        'exp_year': None,
        'verification_value': 'x_card_code',
        'card_type': None,
        #shipping
        'ship_full_name': None,
        'ship_first_name': 'x_ship_to_first_name',
        'ship_last_name': 'x_ship_to_last_name',
        'ship_to_co': 'x_ship_to_company',
        'ship_address': 'x_ship_to_address',
        'ship_address2': None,
        'ship_city': 'x_ship_to_city',
        'ship_state': 'x_ship_to_state',
        'ship_zipcode': 'x_ship_to_zip',
        'ship_country': 'x_ship_to_country',
        #transaction
        'amount': 'x_amount',
        'trans_type': 'x_type',
        'trans_id': 'x_trans_id',
        'alt_trans_id': None,
        'split_tender_id':'x_split_tender_id',
        'is_partial':'x_allow_partial_auth',
    }

    # Response Code: 1 = Approved, 2 = Declined, 3 = Error, 4 = Held for Review
    # AVS Responses: A = Address (Street) matches, ZIP does not,  P = AVS not applicable for this transaction,
    # AVS Responses (cont'd): W = Nine digit ZIP matches, Address (Street) does not, X = Address (Street) and nine digit ZIP match, 
    # AVS Responses (cont'd): Y = Address (Street) and five digit ZIP match, Z = Five digit ZIP matches, Address (Street) does not
    # response index keys to map the value to its proper dictionary key
    RESPONSE_KEYS = {
        '0':'response_code',
        '2':'response_reason_code',
        '3':'response_text',
        '4':'auth_code',
        '5':'avs_response', 
        '6':'trans_id',
        '9':'amount',
        '11':'trans_type',
        '12':'alt_trans_id',
        '38':'cvv_response',
        '43':'amount',
        '53':'split_tender_id',
        '54':'requested_amount',
        '55':'balance_on_card',
        #'n/a':'alt_trans_id2', <-- third way of id'ing a transaction
    }

    debug = False
    test = False

    def __init__(self, username='test', password='testpassword', debug=False, test=False, delim=None):
        """
        setting up object so we can run 4 different ways (live, debug, test & debug+test)
        """
        super(AuthorizeNet, self).set('x_login', username)
        super(AuthorizeNet, self).set('x_tran_key', password)

        # passing fields to bubble up to Base Class
        super(AuthorizeNet, self).__init__(translations=self.REQUEST_FIELDS, debug=debug)

        if debug:
            self.debug = True

        if test:
            self.test = True
            if self.debug: 
                debug_string = " paython.gateways.authorize_net.__init__() -- You're in test mode (& debug, obviously) "
                print debug_string.center(80, '=')

        if delim:
            self.DELIMITER = delim

    def charge_setup(self):
        """
        standard setup, used for charges
        """
        super(AuthorizeNet, self).set('x_delim_data', 'TRUE')
        super(AuthorizeNet, self).set('x_delim_char', self.DELIMITER)
        super(AuthorizeNet, self).set('x_version', self.VERSION)
        if self.debug: 
            debug_string = " paython.gateways.authorize_net.charge_setup() Just set up for a charge "
            print debug_string.center(80, '=')

    def auth(self, amount, credit_card=None, billing_info=None, shipping_info=None, is_partial=False, split_id=None):
        """
        Sends charge for authorization based on amount
        """
        #set up transaction
        self.charge_setup() # considering turning this into a decorator?

        #setting transaction data
        super(AuthorizeNet, self).set(self.REQUEST_FIELDS['amount'], amount)
        super(AuthorizeNet, self).set(self.REQUEST_FIELDS['trans_type'], 'AUTH_ONLY')

        # support for partial auths
        if is_partial:
            super(AuthorizeNet, self).set(self.REQUEST_FIELDS['is_partial'], 'true')
            super(AuthorizeNet, self).set(self.REQUEST_FIELDS['split_tender_id'], split_id)

        # validating or building up request
        if not credit_card:
            if self.debug: 
                debug_string = "paython.gateways.authorize_net.auth()  -- No CreditCard object present. You passed in %s " % (credit_card)
                print debug_string

            raise MissingDataError('You did not pass a CreditCard object into the auth method')
        else:
            super(AuthorizeNet, self).use_credit_card(credit_card)

        if billing_info:
            super(AuthorizeNet, self).set_billing_info(**billing_info)

        if shipping_info:
            super(AuthorizeNet, self).set_shipping_info(**shipping_info)

        # send transaction to gateway!
        response, response_time = self.request()
        return self.parse(response, response_time)

    def settle(self, amount, trans_id, split_id=None):
        """
        Sends prior authorization to be settled based on amount & trans_id PRIOR_AUTH_CAPTURE
        """
        #set up transaction
        self.charge_setup() # considering turning this into a decorator?

        #setting transaction data
        super(AuthorizeNet, self).set(self.REQUEST_FIELDS['trans_type'], 'PRIOR_AUTH_CAPTURE')
        super(AuthorizeNet, self).set(self.REQUEST_FIELDS['amount'], amount)
        super(AuthorizeNet, self).set(self.REQUEST_FIELDS['trans_id'], trans_id)

        if split_id: # settles the entire split
            super(AuthorizeNet, self).set(self.REQUEST_FIELDS['split_tender_id'], split_id)
            super(AuthorizeNet, self).unset(self.REQUEST_FIELDS['trans_id'])

        # send transaction to gateway!
        response, response_time = self.request()
        return self.parse(response, response_time)

    def capture(self, amount, credit_card=None, billing_info=None, shipping_info=None):
        """
        Sends transaction for capture (same day settlement) based on amount.
        """
        #set up transaction
        self.charge_setup() # considering turning this into a decorator?

        #setting transaction data
        super(AuthorizeNet, self).set(self.REQUEST_FIELDS['amount'], amount)
        super(AuthorizeNet, self).set(self.REQUEST_FIELDS['trans_type'], 'AUTH_CAPTURE')

        # validating or building up request
        if not credit_card:
            if self.debug: 
                debug_string = "paython.gateways.authorize_net.capture()  -- No CreditCard object present. You passed in %s " % (credit_card)
                print debug_string

            raise MissingDataError('You did not pass a CreditCard object into the auth method')
        else:
            super(AuthorizeNet, self).use_credit_card(credit_card)

        if billing_info:
            super(AuthorizeNet, self).set_billing_info(**billing_info)

        if shipping_info:
            super(AuthorizeNet, self).set_shipping_info(**shipping_info)

        # send transaction to gateway!
        response, response_time = self.request()
        return self.parse(response, response_time)

    def void(self, trans_id, split_id=None):
        """
        Sends a transaction to be voided (in full)
        """
        #set up transaction
        self.charge_setup() # considering turning this into a decorator?

        #setting transaction data
        super(AuthorizeNet, self).set(self.REQUEST_FIELDS['trans_type'], 'VOID')
        super(AuthorizeNet, self).set(self.REQUEST_FIELDS['trans_id'], trans_id)

        if split_id: # voids an entire split (alternatively, a trans_id just kills that particular txn)
            super(AuthorizeNet, self).set(self.REQUEST_FIELDS['split_tender_id'], split_id)
            super(AuthorizeNet, self).unset(self.REQUEST_FIELDS['trans_id'])

        # send transaction to gateway!
        response, response_time = self.request()
        return self.parse(response, response_time)

    def credit(self, amount, trans_id, credit_card, split_id=None):
        """
        Sends a transaction to be refunded (partially or fully)
        """
        #set up transaction
        self.charge_setup() # considering turning this into a decorator?

        #setting transaction data
        super(AuthorizeNet, self).set(self.REQUEST_FIELDS['trans_type'], 'CREDIT')
        super(AuthorizeNet, self).set(self.REQUEST_FIELDS['trans_id'], trans_id)
        super(AuthorizeNet, self).set(self.REQUEST_FIELDS['number'], credit_card.number)

        if amount: #check to see if we should send an amount
            super(AuthorizeNet, self).set(self.REQUEST_FIELDS['amount'], amount)

        if split_id: # voids an entire split (alternatively, a trans_id just kills that particular txn)
            super(AuthorizeNet, self).set(self.REQUEST_FIELDS['split_tender_id'], split_id)            
            super(AuthorizeNet, self).unset(self.REQUEST_FIELDS['trans_id'])

        # send transaction to gateway!
        response, response_time = self.request()
        return self.parse(response, response_time)

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
            debug_string = " paython.gateways.authorize_net.request() -- Attempting request to: "
            print debug_string.center(80, '=')
            debug_string = "\n %s with params: %s" % (url, super(AuthorizeNet, self).query_string())
            print debug_string

        # make the request
        start = time.time() # timing it
        response = super(AuthorizeNet, self).make_request(url)
        end = time.time() # done timing it
        response_time = '%0.2f' % (end-start)

        if self.debug: # debugging makes code look so nasty
            debug_string = " paython.gateways.authorize_net.request()  -- Request completed in %ss " % response_time
            print debug_string.center(80, '=')

        return response, response_time

    def parse(self, response, response_time):
        """
        On Specific Gateway due differences in response from gateway
        """
        if self.debug: # debugging is so gross
            debug_string = " paython.gateways.authorize_net.parse() -- Raw response: "
            print debug_string.center(80, '=')
            debug_string = "\n %s" % response
            print debug_string

        #splitting up response into a list so we can map it to Paython generic response
        response = response.split(self.DELIMITER)
        approved = True if response[0] == '1' else False

        if self.debug: # :& gonna puke
            debug_string = " paython.gateways.authorize_net.parse() -- Response as list: " 
            print debug_string.center(80, '=')
            debug_string = '\n%s' % response
            print debug_string

        return super(AuthorizeNet, self).standardize(response, self.RESPONSE_KEYS, response_time, approved)
