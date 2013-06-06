import time
import urlparse

from paython.exceptions import MissingDataError
from paython.lib.api import PostGateway

class USAePay(PostGateway):
    """ usaepay.com Payment Gatway Interface

    Based on the CGI Transaction Gateway API v2.17.1
    
    The method names used should be consistent with the Authorize.net terms,
    which are not always the same as those used by USAePay.

    - @auth : Credit Card Authorization
    - @capture : Credit Card Authorization + Automatically marks transaction for settlement
    - @settle : Settle a specific transaction
    - @adjust : Adjust the amount of a previous transaction
    - @void : Cancels the most recent transaction operation (auth, postauth, or return) of the given orderID
    - @credit : Credits funds to card info provided
    - @open_credit : Refund to card provided, not linked to previous transaction
    """

    # This is how we translate the common Paython fields to Gateway specific fields
    REQUEST_FIELDS = {
        #contact
        'full_name' : 'UMname',
        'first_name': None,
        'last_name': None,
        'email': 'UMcustemail',
        'phone': 'UMbillphone',
        #billing
        'address': 'UMbillstreet',
        'address2': 'UMbillstreet2',
        'city': 'UMbillcity',
        'state': 'UMbillstate', 
        'zipcode': 'UMbillzip',
        'country': 'UMbillcountry',
        'ip': 'UMip',
        #card
        'number': 'UMcard',
        'exp_date': 'UMexpir',
        'exp_month': None,
        'exp_year': None,
        'verification_value': 'UMcvv2',
        'card_type': None,
        #shipping
        'ship_full_name': None,
        'ship_first_name': 'UMshipfname',
        'ship_last_name': 'UMshiplname',
        'ship_to_co': 'UMshipcompany',
        'ship_address': 'UMshipstreet',
        'ship_address2': 'UMshipstreet2',
        'ship_city': 'UMshipcity',
        'ship_state': 'UMshipstate',
        'ship_zipcode': 'UMshipzip',
        'ship_country': 'UMshipcountry',
        #transation
        'amount': 'UMamount',
        'trans_type': 'UMcommand',
        'trans_id': 'UMrefNum',
        'alt_trans_id': None,
    }

    # Response Code: 1 = Approved, 2 = Declined, 3 = Error, 4 = Held for Review
    # AVS Responses: A = Address (Street) matches, ZIP does not,  P = AVS not applicable for this transaction,
    # AVS Responses (cont'd): W = Nine digit ZIP matches, Address (Street) does not, X = Address (Street) and nine digit ZIP match, 
    # AVS Responses (cont'd): Y = Address (Street) and five digit ZIP match, Z = Five digit ZIP matches, Address (Street) does not
    # response index keys to map the value to its proper dictionary key
    RESPONSE_KEYS = {
        'UMresult' :         'response_code',
        'UMerror' :          'response_text',
        'UMauthCode' :       'auth_code',
        'UMavsResult' :      'avs_response', 
        'UMrefNum' :         'trans_id',
        'UMauthAmount' :     'amount',
        'UMcvv2ResultCode' : 'cvv_response',
        'UMavsResult' :      'avs_response_text', 
        #'n/a' :              'response_reason_code',
        #'n/a' :              'trans_type',
        #'n/a' :              'alt_trans_id',
        #'n/a' :              'response_reason',
        #'n/a' :              'fraud_level',
    }

    def __init__(self, username='test', password='testpassword', debug=False, test=False):
        """
        setting up object so we can run 4 different ways (live, debug, test & debug+test)
        """
        # passing fields to bubble up to Base Class
        super(USAePay, self).__init__(translations=self.REQUEST_FIELDS, debug=debug)

        self.set('UMkey', username)
        #self.set('UM', password)

        self.API_URI = {
                        False : 'https://www.usaepay.com/gate',
                        True :  'https://sandbox.usaepay.com/gate'
                       }

        self.test = test
        if test:
            if self.debug: 
                debug_string = self._get_debug_str_base() + ".__init__() -- You're in test mode (& debug, obviously) "
                print debug_string.center(80, '=')

    def _get_debug_str_base(self):
        return ' ' + __name__ + '.' + self.__class__.__name__
        
    def charge_setup(self):
        """
        standard setup, used for charges
        """
        #self.set('x_delim_data', 'TRUE')
        #self.set('x_delim_char', self.DELIMITER)
        #self.set('x_version', self.VERSION)
        if self.debug: 
            debug_string = self._get_debug_str_base() + '.charge_setup() Just set up for a charge '
            print debug_string.center(80, '=')

    def auth(self, amount, credit_card=None, billing_info=None, shipping_info=None):
        """
        Sends charge for authorization based on amount
        """
        #set up transaction
        self.charge_setup()

        #setting transaction data
        self.set(self.REQUEST_FIELDS['amount'], amount)
        self.set(self.REQUEST_FIELDS['trans_type'], 'cc:authonly')

        # validating or building up request
        if not credit_card:
            if self.debug: 
                debug_string = self._get_debug_str_base() + '.auth()  -- No CreditCard object present. You passed in %s ' % (credit_card)
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
        return self.parse(response, response_time)

    def settle(self, amount, trans_id):
        """
        Sends prior authorization to be settled based on amount & trans_id
        """
        #set up transaction
        self.charge_setup() 

        #setting transaction data
        self.set(self.REQUEST_FIELDS['trans_type'], 'cc:capture')
        self.set(self.REQUEST_FIELDS['amount'], amount)
        self.set(self.REQUEST_FIELDS['trans_id'], trans_id)

        # send transaction to gateway!
        response, response_time = self.request()
        return self.parse(response, response_time)

    def adjust(self, amount, trans_id):
        """
        Adjust an existing (unsettled) sale.  Adjust the amount up or down, etc.
        """
        #set up transaction
        self.charge_setup() 

        #setting transaction data
        self.set(self.REQUEST_FIELDS['trans_type'], 'cc:adjust')
        self.set(self.REQUEST_FIELDS['amount'], amount)
        self.set(self.REQUEST_FIELDS['trans_id'], trans_id)

        # send transaction to gateway!
        response, response_time = self.request()
        return self.parse(response, response_time)

    def capture(self, amount, credit_card=None, billing_info=None, shipping_info=None):
        """
        Sends transaction for capture (same day settlement) based on amount.
        """
        #set up transaction
        self.charge_setup()

        #setting transaction data
        self.set(self.REQUEST_FIELDS['amount'], amount)
        self.set(self.REQUEST_FIELDS['trans_type'], 'cc:sale')

        # validating or building up request
        if not credit_card:
            if self.debug: 
                debug_string = self._get_debug_str_base() + 'capture()  -- No CreditCard object present. You passed in ' + str(credit_card)
                print debug_string

            raise MissingDataError('You did not pass a CreditCard object into the auth method')
        else:
            self.use_credit_card(credit_card)

        if billing_info:
            self.set_billing_info(**billing_info)

        if shipping_info:
            self.set_shipping_info(**shipping_info)

        # send transaction to gateway
        response, response_time = self.request()
        return self.parse(response, response_time)

    def void(self, trans_id):
        """
        Sends a transaction to be voided (in full)
        """
        #set up transaction
        self.charge_setup()

        #setting transaction data
        self.set(self.REQUEST_FIELDS['trans_type'], 'void')
        self.set(self.REQUEST_FIELDS['trans_id'], trans_id)

        # send transaction to gateway
        response, response_time = self.request()
        return self.parse(response, response_time)

    def credit(self, amount, trans_id, credit_card):
        """
        Sends a transaction to be refunded (partially or fully)
        """
        #set up transaction
        self.charge_setup()

        #setting transaction data
        self.set(self.REQUEST_FIELDS['trans_type'], 'refund')
        self.set(self.REQUEST_FIELDS['trans_id'], trans_id)
        self.set(self.REQUEST_FIELDS['number'], credit_card.number)

        if amount: #check to see if we should send an amount
            self.set(self.REQUEST_FIELDS['amount'], amount)

        # send transaction to gateway
        response, response_time = self.request()
        return self.parse(response, response_time)

    def open_credit(self, amount, credit_card):
        """
        Refund money to a credit card, not linked to a previous transaction
        """
        #set up transaction
        self.charge_setup()

        #setting transaction data
        self.set(self.REQUEST_FIELDS['trans_type'], 'cc:credit')
        self.set(self.REQUEST_FIELDS['number'], credit_card.number)

        if amount: #check to see if we should send an amount
            self.set(self.REQUEST_FIELDS['amount'], amount)

        # send transaction to gateway
        response, response_time = self.request()
        return self.parse(response, response_time)

    def request(self):
        """
        Makes a request using lib.api.GetGateway.make_request() & move some debugging away from other methods.
        """
        # decide which url to use (test|live)
        url = self.API_URI[self.test]

        if self.debug:
            debug_string = self._get_debug_str_base() + '.request() -- Attempting request to: '
            print debug_string.center(80, '=')
            debug_string = "\n %s with params: %s" % (url, self.params())
            print debug_string

        # make the request
        start = time.time() # timing it
        response = self.make_request(url)
        end = time.time() # done timing it
        response_time = '%0.2f' % (end-start)

        if self.debug: 
            debug_string = self._get_debug_str_base() + '.request()  -- Request completed in ' + response_time + 's '
            print debug_string.center(80, '=')

        return response, response_time

    def parse(self, response, response_time):
        """
        On Specific Gateway due differences in response from gateway
        """
        if self.debug:
            debug_string = self._get_debug_str_base() + '.parse() -- Raw response: '
            print debug_string.center(80, '=')
            debug_string = '\n ' + str(response)
            print debug_string

        #splitting up response into a list so we can map it to Paython generic response
        new_response = urlparse.parse_qsl(response)
        response = dict(new_response)
        approved = (response['UMresult'] == 'A')

        if self.debug:
            debug_string = self._get_debug_str_base() + '.parse() -- Response as list: ' 
            print debug_string.center(80, '=')
            debug_string = '\n' + str(response)
            print debug_string

        return self.standardize(response, self.RESPONSE_KEYS, response_time, approved)