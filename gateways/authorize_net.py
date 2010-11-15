from Paython.exceptions import *
import time

from Paython.lib.api import GetGateway

class AuthorizeNet(GetGateway):
    """TODO needs docstring"""
    VERSION = '3.1'
    DELIMITER = ';'

    # This is how we determine whether or not we allow 'test' as an init param
    API_URI = {
        'live' : 'https://secure.authorize.net/gateway/transact.dll',
        'test' : 'https://test.authorize.net/gateway/transact.dll'
    }

    # This is how we translate the common Paython fields to Gateway specific fields & do validation
    REQUEST_FIELDS = {
        #contact
        'first_name': {'f_name':'x_first_name', 'required': True},
        'last_name': {'f_name': 'x_last_name', 'required': True},
        'email': {'f_name': 'x_email', 'required': True},
        'phone': {'f_name': 'x_phone', 'required': False},
        #billing
        'address': {'f_name': 'x_address', 'required': False},
        'city': {'f_name': 'x_city', 'required': True},
        'state': {'f_name': 'x_state', 'required': True},
        'zipcode': {'f_name': 'x_zip', 'required': True},
        'country': {'f_name': 'x_country', 'required': False},
        'ip': {'f_name': 'x_customer_ip', 'required': True},
        #card
        'number': {'f_name': 'x_card_num', 'required': True},
        'exp_date': {'f_name': 'x_exp_date', 'required': True},
        'verification_value': {'f_name': 'x_card_code', 'required': False},
        #shipping
        'ship_first_name': {'f_name': 'x_ship_to_first_name', 'required': False},
        'ship_last_name': {'f_name': 'x_ship_to_last_name', 'required': False},
        'ship_to_co': {'f_name': 'x_ship_to_company', 'required': False},
        'ship_address': {'f_name': 'x_ship_to_address', 'required': False},
        'ship_city': {'f_name': 'x_ship_to_city', 'required': False},
        'ship_state': {'f_name': 'x_ship_to_state', 'required': False},
        'ship_zipcode': {'f_name': 'x_ship_to_zip', 'required': False},
        'ship_country': {'f_name': 'x_ship_to_country', 'required': False},
        #transation
        'amount': {'f_name':'x_amount', 'required': False},
        'trans_type': {'f_name':'x_type', 'required': False},
    }

    # Response Code: 1 = Approved, 2 = Declined, 3 = Error, 4 = Held for Review
    # AVS Responses: A = Address (Street) matches, ZIP does not,  P = AVS not applicable for this transaction,
    # AVS Responses (cont'd): W = Nine digit ZIP matches, Address (Street) does not, X = Address (Street) and nine digit ZIP match, 
    # AVS Responses (cont'd): Y = Address (Street) and five digit ZIP match, Z = Five digit ZIP matches, Address (Street) does not
    # response index keys to map the value to its proper dictionary key
    RESPONSE_KEYS = {
        '1':'response_code',
        '3':'response_reason_code',
        '4':'response_text',
        '5':'auth_code',
        '6':'avs_response', 
        '7':'trans_id',
        '10':'amount',
        '12':'trans_type',
        '13':'alt_trans_id',
        '39':'cvv_response',
        '44':'amount',
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

        if delim:
            self.DELIMITER = delim

    def charge_setup(self):
        """
        standard setup, used for charges
        """
        super(AuthorizeNet, self).set('x_delim_data', 'TRUE')
        if self.debug: 
            debug_string = " Just set up for a charge "
            print debug_string.center(80, '=')

    def auth(self, amount, credit_card=None, billing_info=None, shipping_info=None):
        """
        Sends charge for authorization based on amount
        """
        #set up transaction
        self.charge_setup()

        #setting transaction data
        super(AuthorizeNet, self).set(self.REQUEST_FIELDS['amount']['f_name'], amount)
        super(AuthorizeNet, self).set(self.REQUEST_FIELDS['trans_type']['f_name'], 'AUTH_ONLY')

        # validating or building up request
        if not credit_card:
            if self.debug: 
                debug_string = " No CreditCard object present. You passed in %s " % (credit_card)
                print debug_string.center(80, '=')

            raise MissingDataError('You did not pass a CreditCard object into the auth method')
        else:
            super(AuthorizeNet, self).use_credit_card(credit_card)

        if billing_info:
            super(AuthorizeNet, self).set_billing_info(billing_info)

        if shipping_info:
            super(AuthorizeNet, self).set_shipping_info(shipping_info)

        # decide which url to use (test|live)
        if self.test:
            url = self.API_URI['test'] # here just in case we want to granularly change endpoint

            if self.debug: 
                debug_string = " You're in test mode (& debug, obviously) "
                print debug_string.center(80, '=')
        else:
            url = self.API_URI['live'] 

        # make the request
        start = time.time() # timing it

        if self.debug: 
            debug_string = " Attempting request to: %s" % (url)
            print debug_string.center(80, '=')
            debug_string = "\n With params: %s" % (super(AuthorizeNet, self).query_string())
            print debug_string

        response = super(AuthorizeNet, self).make_request(url)

        end = time.time() # done timing it
        response_time = '%0.2f' % (end-start)

        if self.debug: 
            debug_string = " Request completed in %s seconds " % response_time
            print debug_string.center(80, '=')

        return self.parse(response, response_time)

    def parse(self, response, response_time):
        """
        On Specific Gateway due differences in response from gateway
        """
        if self.debug: 
            debug_string = " Raw response: "
            print debug_string.center(80, '=')
            debug_string = "\n %s" % response
            print debug_string

        response = '%s%s' % (self.DELIMITER, response)
        response = response.split(self.DELIMITER)
        approved = True if response[1] == '1' else False

        if self.debug: 
            debug_string = " Response as list: " 
            print debug_string.center(80, '=')
            debug_string = '\n%s' % response
            print debug_string

        return super(AuthorizeNet, self).standardize(response, self.RESPONSE_KEYS, response_time, approved)