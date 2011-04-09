import re
import time
import urlparse

from paython.exceptions import DataValidationError, MissingDataError
from paython.lib.api import XMLGateway

class FirstDataLegacy(XMLGateway):
    """First data legacy support"""

    # This is how we determine whether or not we allow 'test' as an init param
    API_URI = {
        'live' : 'https://secure.linkpt.net/LSGSXML'
    }

    # This is how we translate the common Paython fields to Gateway specific fields
    # it goes like this: 'paython_key' ==> 'gateway_specific_parameter'
    REQUEST_FIELDS = {
        #contact
        'full_name': 'order/billing/name',
        'first_name': None,
        'last_name': None,
        'email': 'order/billing/email',
        'phone': 'order/billing/phone',
        #billing
        'address': 'order/billing/address1',
        'address2': 'order/billing/address2',
        'city': 'order/billing/city',
        'state': 'order/billing/state', 
        'zipcode': 'order/billing/zip',
        'country': 'order/billing/country',
        'ip': 'order/transactiondetails/ip',
        #card
        'number': 'order/creditcard/cardnumber',
        'exp_date': None,
        'exp_month': 'order/creditcard/cardexpmonth',
        'exp_year': 'order/creditcard/cardexpyear',
        'verification_value': 'order/creditcard/cvmvalue',
        'card_type': None,
        #shipping
        'ship_full_name': 'order/shipping/name',
        'ship_first_name': None,
        'ship_last_name': None,
        'ship_to_co': None,
        'ship_address': 'order/shipping/address1',
        'ship_address2': 'order/shipping/address2',
        'ship_city': 'order/shipping/city',
        'ship_state': 'order/shipping/state',
        'ship_zipcode': 'order/shipping/zip',
        'ship_country': 'order/shipping/country',
        #transation
        'amount': 'order/payment/chargetotal',
        'trans_type': 'order/orderoptions/ordertype',
        'trans_id': 'order/transactiondetails/oid',
        'alt_trans_id': None,
    }

    # Response Code: 1 = Approved, 2 = Declined, 3 = Error, 4 = Held for Review
    # AVS Responses: A = Address (Street) matches, ZIP does not,  P = AVS not applicable for this transaction,
    # AVS Responses (cont'd): W = Nine digit ZIP matches, Address (Street) does not, X = Address (Street) and nine digit ZIP match, 
    # AVS Responses (cont'd): Y = Address (Street) and five digit ZIP match, Z = Five digit ZIP matches, Address (Street) does not
    # AVS Responses (cont'd): N = Neither the street address nor the postal code matches. R = Retry, System unavailable (maybe due to timeout)
    # AVS Responses (cont'd): S = Service not supported. U = Address information unavailable. E = Data not available/error invalid. 
    # AVS Responses (cont'd): G = Non-US card issuer that does not participate in AVS
    # response index keys to map the value to its proper dictionary key
    # it goes like this: 'gateway_specific_parameter' ==> 'paython_key'
    RESPONSE_KEYS = {
        'r_message':'response_text',
        'r_authresponse':'auth_code',
        'r_avs':'avs_response', 
        'r_ordernum':'trans_id',
        'r_ref':'alt_trans_id',
        #'fulltotal':'amount', <-- amount of transaction
        #'trantype':'trans_type', <-- type of transaction
        #'ordernumber':'alt_trans_id2', <-- third way of id'ing a transaction
        #'38':'cvv_response', <-- way of finding out if verification_value is invalid
        #'2':'response_reason_code', <-- mostly for reporting
        #'0':'response_code', <-- mostly for reporting
    }

    debug = False
    test = False
    cvv_present = False

    def __init__(self, username='Test123', key_file='../keys/yourkey.pem', cert_file='../keys/yourkey.pem', debug=False, test=False):
        """
        Setting up object so we can run 4 different ways (live, debug, test & debug+test) - no password because gateway does not use it
        """
        # passing fields to bubble up to Base Class
        ssl_config = {'port':'1129', 'key_file':key_file, 'cert_file':cert_file}
        # there is only a live environment, with test credentials & we only need the host for now
        url = urlparse.urlparse(self.API_URI['live']).netloc.split(':')[0]
        # initing the XML gateway
        super(FirstDataLegacy, self).__init__(url, translations=self.REQUEST_FIELDS, debug=debug, special_params=ssl_config)

        #setting some creds
        super(FirstDataLegacy, self).set('order/merchantinfo/configfile', username)

        if debug:
            self.debug = True

        if test:
            self.test = True
            if self.debug: 
                debug_string = " paython.gateways.firstdata_legacy.__init__() -- You're in test mode (& debug, obviously) "
                print debug_string.center(80, '=')

    def charge_setup(self):
        """
        standard setup, used for charges
        """
        if self.cvv_present:
            super(FirstDataLegacy, self).set('order/creditcard/cvmindicator', 'provided')
        
        if self.test: # will almost always return nice
            super(FirstDataLegacy, self).set('order/orderoptions/result', 'Good')
        else:
            super(FirstDataLegacy, self).set('order/orderoptions/result', 'Live')
        
        if self.debug: 
            debug_string = " paython.gateways.firstdata_legacy.charge_setup() Just set up for a charge "
            print debug_string.center(80, '=')

    def auth(self, amount, credit_card=None, billing_info=None, shipping_info=None):
        """
        Sends charge for authorization based on amount
        """
        #check for cvv
        self.cvv_present = True if credit_card.verification_value else False
        #set up transaction
        self.charge_setup() # considering turning this into a decorator?

        #setting transaction data
        super(FirstDataLegacy, self).set(self.REQUEST_FIELDS['amount'], amount)
        super(FirstDataLegacy, self).set(self.REQUEST_FIELDS['trans_type'], 'Preauth')
        #special treatment to make peoples lives easier (extracting addrnum from address)
        try:
            matches = re.match('\d+', billing_info['address'])
        except KeyError:
            raise DataValidationError('Unable to find a billing address to extract a number from for gateway')
        
        if matches:
            super(FirstDataLegacy, self).set('order/billing/addrnum', matches.group()) #hardcoded because of uniqueness to gateway
        else:
            raise DataValidationError('Unable to find a number at the start of provided billing address')

        # validating or building up request
        if not credit_card:
            if self.debug: 
                debug_string = "paython.gateways.firstdata_legacy.auth()  -- No CreditCard object present. You passed in %s " % (credit_card)
                print debug_string

            raise MissingDataError('You did not pass a CreditCard object into the auth method')
        else:
            credit_card._exp_yr_style = True
            super(FirstDataLegacy, self).use_credit_card(credit_card)

        if billing_info:
            super(FirstDataLegacy, self).set_billing_info(**billing_info)

        if shipping_info:
            super(FirstDataLegacy, self).set_shipping_info(**shipping_info)

        # send transaction to gateway!
        response, response_time = self.request()
        return self.parse(response, response_time)

    def settle(self, amount, trans_id):
        """
        Sends prior authorization to be settled based on amount & trans_id PRIOR_AUTH_CAPTURE
        """
        #set up transaction
        self.charge_setup() # considering turning this into a decorator?

        #setting transaction data
        super(FirstDataLegacy, self).set(self.REQUEST_FIELDS['trans_type'], 'Postauth')
        super(FirstDataLegacy, self).set(self.REQUEST_FIELDS['amount'], amount)
        super(FirstDataLegacy, self).set(self.REQUEST_FIELDS['trans_id'], trans_id)

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
        super(FirstDataLegacy, self).set(self.REQUEST_FIELDS['amount'], amount)
        super(FirstDataLegacy, self).set(self.REQUEST_FIELDS['trans_type'], 'Sale')

        #special treatment to make peoples lives easier (extracting addrnum from address)
        matches = re.match('\d+', billing_info['address'])
        if matches:
            super(FirstDataLegacy, self).set('order/billing/addrnum', matches.group()) #hardcoded because of uniqueness to gateway
        else:
            raise DataValidationError('Unable to find a number at the start of provided billing address')

        # validating or building up request
        if not credit_card:
            if self.debug: 
                debug_string = "paython.gateways.firstdata_legacy.capture()  -- No CreditCard object present. You passed in %s " % (credit_card)
                print debug_string

            raise MissingDataError('You did not pass a CreditCard object into the auth method')
        else:
            credit_card._exp_yr_style = True
            super(FirstDataLegacy, self).use_credit_card(credit_card)

        if billing_info:
            super(FirstDataLegacy, self).set_billing_info(**billing_info)

        if shipping_info:
            super(FirstDataLegacy, self).set_shipping_info(**shipping_info)

        # send transaction to gateway!
        response, response_time = self.request()
        return self.parse(response, response_time)

    def void(self, trans_id):
        """
        Send a SALE (only works for sales) transaction to be voided (in full) that was initially sent for capture the same day
        This is so wierd!
        """
        #set up transaction
        self.charge_setup() # considering turning this into a decorator?

        #setting transaction data
        super(FirstDataLegacy, self).set(self.REQUEST_FIELDS['trans_type'], 'Void')
        super(FirstDataLegacy, self).set(self.REQUEST_FIELDS['trans_id'], trans_id)

        # send transaction to gateway!
        response, response_time = self.request()
        return self.parse(response, response_time)

    def credit(self, amount, trans_id, credit_card):
        """
        Sends a transaction to be refunded (partially or fully)
        """
        #set up transaction
        self.charge_setup() # considering turning this into a decorator?

        #setting transaction data
        super(FirstDataLegacy, self).set(self.REQUEST_FIELDS['trans_type'], 'Credit')
        super(FirstDataLegacy, self).set(self.REQUEST_FIELDS['trans_id'], trans_id)
        super(FirstDataLegacy, self).set(self.REQUEST_FIELDS['number'], credit_card.number)

        if amount: #check to see if we should send an amount
            super(FirstDataLegacy, self).set(self.REQUEST_FIELDS['amount'], amount)

        # send transaction to gateway!
        response, response_time = self.request()
        return self.parse(response, response_time)

    def request(self):
        """
        Makes a request using lib.api.XMLGateway.make_request() & move some debugging away from other methods.
        """
        #getting the uri to POST xml to
        uri = urlparse.urlparse(self.API_URI['live']).path

        if self.debug:  # I wish I could hide debugging
            debug_string = " paython.gateways.firstdata_legacy.request() -- Attempting request to: "
            print debug_string.center(80, '=')
            debug_string = "\n %s with params: %s" % (self.API_URI['live'], super(FirstDataLegacy, self).request_xml())
            print debug_string

        # make the request
        start = time.time() # timing it
        response = super(FirstDataLegacy, self).make_request(uri)
        end = time.time() # done timing it
        response_time = '%0.2f' % (end-start)

        if self.debug: # debugging makes code look so nasty
            debug_string = " paython.gateways.firstdata_legacy.request()  -- Request completed in %ss " % response_time
            print debug_string.center(80, '=')

        return response, response_time

    def parse(self, response, response_time):
        """
        On Specific Gateway due differences in response from gateway
        """
        if self.debug: # debugging is so gross
            debug_string = " paython.gateways.firstdata_legacy.parse() -- Raw response: "
            print debug_string.center(80, '=')
            debug_string = "\n %s" % response
            print debug_string

        response = response['response']
        approved = True if response['r_approved'] == 'APPROVED' else False

        if self.debug: # :& gonna puke
            debug_string = " paython.gateways.firstdata_legacy.parse() -- Response as dict: " 
            print debug_string.center(80, '=')
            debug_string = '\n%s' % response
            print debug_string

        return super(FirstDataLegacy, self).standardize(response, self.RESPONSE_KEYS, response_time, approved)
