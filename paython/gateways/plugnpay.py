import time
import urllib

from paython.exceptions import MissingDataError
from paython.lib.api import PostGateway

class PlugnPay(PostGateway):

    """ plugnpay.com Payment Gatway Interface

    Based on the basic Remote Client Integration Specification Rev. 04.22.2011

    - @auth : Credit Card Authorization
    - @reauth : Used to settle a transaction at a lower dollar amount
    - @capture : Credit Card Authorization + Automatically marks transaction for settlement
    - @settle : Settle a specific transaction
    - @void : Cancels the most recent transaction operation (auth, postauth, or return) of the given orderID
    - @return_transaction : Return funds back to a prior authorization
    - @return_credit : Credits funds, using card info file from a previous transaction
    - @credit : Credits funds to card info provided
    - @query : Ability to query system for credit card transaction information
    """

    API_URI = 'https://pay1.plugnpay.com/payment/pnpremote.cgi'

    DELIMITER = '&'

    # This is how we translate the common Paython fields to Gateway specific fields
    REQUEST_FIELDS = {
        #contact
        'full_name' : 'card-name',
        'first_name': None,
        'last_name': None,
        'email': 'email',
        'phone': 'phone',
        'fax': 'fax',
        #billing
        'address': 'card-address1',
        'address2': 'card-address2',
        'city': 'card-city',
        'state': 'card-state',
        'province': 'card-prov',
        'zipcode': 'card-zip',
        'country': 'card-country',
        'ip': None,
        #card
        'number': 'card-number',
        'exp_date': 'card-exp',
        'exp_month': None,
        'exp_year': None,
        'verification_value': 'card-cvv',
        'card_type': None,
        #shipping
        'ship_full_name': 'shipname',
        'ship_first_name': None,
        'ship_last_name': None,
        'ship_to_co': None,
        'ship_address': 'address1',
        'ship_address2': 'address2',
        'ship_city': 'city',
        'ship_state': 'state',
        'ship_province': 'province',
        'ship_zipcode': 'zip',
        'ship_country': 'country',
        #transation
        'amount': 'card-amount',
        'trans_mode': 'mode',
        'trans_type': 'authtype',
        'trans_id': 'orderID',
        'alt_trans_id': None,
    }

    # AVS response codes by credit card
    # https://pay1.plugnpay.com/admin/doc_replace.cgi?doc=AVS_Specifications.htm
    AVS_RESPONSE_KEYS = {}

    # Visa
    AVS_RESPONSE_KEYS['VISA'] = {
        'A' : 'Address matches, ZIP code does not',
        'B' : 'Street address match for international transaction; postal code not verified',
        'C' : 'Street & postal code not verified for international transaction',
        'D' : 'Street & Postal codes match for international transaction',
        'E' : 'Transaction is ineligible for address verification',
        'F' : 'Street address & postal codes match for international transaction. (UK Only)',
        'G' : 'AVS not performed because the international issuer does not support AVS',
        'I' : 'Address information not verified for international transaction',
        'M' : 'Street address & postal codes match for international transaction',
        'N' : 'Neither the ZIP nor the address matches',
        'P' : 'Postal codes match for international transaction; street address not verified',
        'S' : 'AVS not supported at this time',
        'R' : "Issuer's authorization system is unavailable, try again later",
        'U' : 'Unable to perform address verification because either address information is unavailable or the Issuer does not support AVS',
        'W' : 'Nine-digit zip match, address does not',
        'X' : 'Exact match (nine-digit zip and address)',
        'Y' : 'Address & 5-digit or 9-digit ZIP match',
        'Z' : 'Either 5-digit or 9-digit ZIP matches, address does not',
        '0' : 'No AVS response returned from issuing bank'
    }

    # Mastercard
    AVS_RESPONSE_KEYS['MSTR'] = {
        'A' : 'Address matches, ZIP code does not',
        'B' : 'Street address match for international transaction; postal code not verified',
        'C' : 'Street & postal code not verified for international transaction',
        'D' : 'Street & Postal codes match for international transaction',
        'E' : 'Address verification not allowed for card typ',
        'F' : 'Street address & postal codes match for international transaction. (UK Only',
        'G' : 'International Address information unavailable.',
        'I' : 'Address information not verified for international transaction',
        'M' : 'Street address & postal codes match for international transaction',
        'N' : 'Neither the ZIP nor the address matches',
        'P' : 'Postal codes match for international transaction; street address not verified',
        'S' : 'AVS not supported at this time',
        'R' : 'Retry, system unable to process',
        'U' : 'No data from issuer/BankNet switch',
        'W' : '9-digit ZIP code matches, but address does not',
        'X' : 'Exact, all digits match, 9-digit ZIP code',
        'Y' : 'Exact, all digits match, 5-digit ZIP code',
        'Z' : '5-digit ZIP code matches, but address does not',
        '0' : 'No AVS response returned from issuing bank'
    }

    # American Express
    AVS_RESPONSE_KEYS['AMEX'] = {
        'A' : 'Address only is correc',
        'B' : 'Street address match for international transaction; postal code not verified',
        'C' : 'Street & postal code not verified for international transaction',
        'D' : 'Street & Postal codes match for international transaction',
        'E' : 'Address verification not allowed for card typ',
        'F' : 'Street address & postal codes match for international transaction. (UK Only',
        'G' : 'International Address information unavailable.',
        'I' : 'Address information not verified for international transaction',
        'M' : 'Street address & postal codes match for international transaction',
        'N' : 'Neither the ZIP nor the address matche',
        'P' : 'Street address match for international transaction; postal code not verified',
        'R' : "Issuer's authorization system is unavailable, try again late",
        'S' : 'AVS not supported at this tim',
        'U' : 'The necessary information is not available, account number is neither U.S. nor Canadia',
        'W' : 'Nine-digit zip match, address does not.',
        'X' : 'Exact match (nine-digit zip and address).',
        'Y' : 'Yes, address and ZIP code are both correct',
        'Z' : 'ZIP code only is correc',
        '0' : 'No AVS response returned from issuing bank',
    }

    # Discover
    AVS_RESPONSE_KEYS['SWTCH'] = {
        'A' : 'Address matches, ZIP code does not',
        'B' : 'Street address match for international transaction; postal code not verified',
        'C' : 'Street & postal code not verified for international transaction',
        'D' : 'Street & Postal codes match for international transaction',
        'E' : 'Transaction is ineligible for address verificatio',
        'F' : 'Street address & postal codes match for international transaction. (UK Only',
        'G' : 'AVS not performed because the international issuer does not support AVS',
        'I' : 'Address information not verified for international transaction',
        'M' : 'Street address & postal codes match for international transaction',
        'N' : 'Neither the ZIP nor the address matche',
        'P' : 'Postal codes match for international transaction; street address not verified',
        'S' : 'AVS not supported at this tim',
        'R' : "Issuer's authorization system is unavailable, try again late",
        'U' : 'Unable to perform address verification because either address information is unavailable or the Issuer does not support AV',
        'W' : 'Nine-digit zip match, address does not.',
        'X' : 'Exact match (nine-digit zip and address).',
        'Y' : 'Address & 5-digit or 9-digit ZIP matc',
        'Z' : 'Either 5-digit or 9-digit ZIP matches, address does no',
        '0' : 'No AVS response returned from issuing bank'
    }

    STATUS_RESPONSE_KEYS = {

        # Payment Gateway Response Codes
        'P01' : 'AVS Mismatch Failure',
        'P02' : 'CVV2 Mismatch Failure',
        'P03' : 'Sorry, the transaction failed Cybersource Fraud Test and was voided.',
        'P21' : 'Transaction may not be marked',
        'P22' : 'orderID was not marked successfully.',
        'P30' : 'Test Tran. Bad Card',
        'P35' : 'Test Tran. Problem',
        'P40' : 'Username already exists',
        'P41' : 'Username is blank',
        'P50' : 'Fraud Screen Failure',
        'P51' : 'Missing PIN Code',
        'P52' : 'Invalid Bank Acct. No.',
        'P53' : 'Invalid Bank Routing No.',
        'P54' : 'Invalid/Missing Check No.',
        'P55' : 'Invalid Credit Card No.',
        'P56' : 'Invalid CVV2/CVC2 No.',
        'P57' : 'Expired. CC Exp. Date',
        'P58' : 'Missing Data',
        'P59' : 'Missing Email Address',
        'P60' : 'Zip Code does not match Billing State.',
        'P61' : 'Invalid Billing Zip Code',
        'P62' : 'Zip Code does not match Shipping State.',
        'P63' : 'Invalid Shipping Zip Code',
        'P64' : 'Invalid Credit Card CVV2/CVC2 Format.',
        'P65' : 'Maximum number of attempts has been exceeded.',
        'P66' : 'Credit Card number has been flagged and can not be used to access this service.',
        'P67' : 'IP Address is on Blocked List.',
        'P68' : 'Billing country does not match ipaddress country.',
        'P69' : 'US based ipaddresses are currently blocked.',
        'P70' : 'Credit Cards issued from this country are currently not being accepted.',
        'P71' : 'Credit Cards issued from this bank are currently not being accepted.',
        'P72' : 'Daily volume exceeded.',
        'P73' : 'Too many transactions within allotted time.',
        'P74' : 'Sales for this phone number are currently not being accepted.',
        'P75' : 'Email Address is on Blocked List.',
        'P76' : 'Duplicate Transaction error.',
        'P91' : 'Missing/incorrect password',
        'P92' : 'Account not configured for mobil administration',
        'P93' : 'IP Not registered to username.',
        'P94' : 'Mode not permitted for this account.',
        'P95' : 'Currently Blank',
        'P96' : 'Currently Blank',
        'P97' : 'Processor not responding',
        'P98' : 'Missing merchant/publisher name',
        'P99' : 'Currently Blank',
        'P100' : 'Discount exceeds available gift certificate balance.',
        'P101' : 'Gift certificate discount does not match order.',

        # VisaNet / Vital Response Codes
        '00' : 'Approved',
        '01' : 'Refer to issuer',
        '02' : 'Refer to issuer',
        '28' : 'File is temporarily unavailable',
        '91' : 'Issuer or switch is unavailable',
        '04' : 'Pick up card',
        '07' : 'Pick up card',
        '41' : 'Pick up card - lost',
        '43' : 'Pick up card - stolen',
        'EA' : 'Verification error',
        '79' : 'Already reversed at switch',
        '13' : 'Invalid amount',
        '83' : 'Can not verify PIN',
        '86' : 'Can not verify PIN',
        '14' : 'Invalid card number',
        '82' : 'Cashback limit exceeded',
        'N3' : 'Cashback service not available',
        'EB' : 'Verification error',
        'EC' : 'Verification error',
        '80' : 'Invalid date',
        '05' : 'Do not honor',
        '51' : 'Insufficient funds',
        'N4' : 'Exceeds issuer withdrawal limit',
        '61' : 'Exceeds withdrawal limit',
        '62' : 'Invalid service code, restricted',
        '65' : 'Activity limit exceeded',
        '93' : 'Violation, cannot complete',
        '81' : 'Cryptographic error',
        '06' : 'General error',
        '54' : 'Expired card',
        '92' : 'Destination not found',
        '12' : 'Invalid transaction',
        '78' : 'No account',
        '21' : 'unable to back out transaction',
        '76' : 'Unable to locate, no match',
        '77' : 'Inconsistent date, rev. or repeat',
        '52' : 'No checking account',
        '39' : 'No credit account',
        '53' : 'No savings account',
        '15' : 'No such issuer',
        '75' : 'PIN tries exceeded',
        '19' : 'Re-enter transaction',
        '63' : 'Security violation',
        '57' : 'Trans. not permitted-Card',
        '58' : 'Trans. not permitted-Terminal',
        '96' : 'System malfunction',
        '03' : 'Invalid merchant ID',
        '55' : 'Incorrect PIN',
        'N7' : 'CVV2 Value supplied is invalid',
        'xx' : 'Undefined response',
        'CV' : 'Card type verification error',
        'R1' : 'Stop recurring'
    }

    SIMPLE_STATUS_RESPONSE_KEYS = {
        'A' : 'Approved',
        'C' : 'Call Auth Center',
        'D' : 'Declined',
        'P' : 'Pick up card',
        'X' : 'Expired',
        'E' : 'Other Error'
    }

    RESPONSE_KEYS = {
        'sresp' : 'response_code',
        'sresp-msg':'response_text',
        'resp-code-msg' : 'response_reason',
        'resp-code' : 'response_reason_code',
        'auth-code':'auth_code',
        'avs-code':'avs_response', 
        'avs-code-msg':'avs_response_text', 
        'orderID':'trans_id',
        'card-amount':'amount',
        'authtype':'trans_type',
        'merchfraudlev' : 'fraud_level',
        'alt_trans_id' : 'ref_number' # refnumber
    }

    debug = False

    def __init__(self, username='pnpdemo', password='', email='', dontsndmail=True, debug=True):

        # mandatory fields for every request
        super(PlugnPay, self).set('publisher-name', username)
        if password: # optional gateway password
            super(PlugnPay, self).set('publisher-password', password)

        if email: # publisher email to send alerts/notifiation to
            super(PlugnPay, self).set('publisher-email', email)

        # don't send transaction confirmation email to customer
        if dontsndmail:
            super(PlugnPay, self).set('dontsndmail', 'yes')

        if debug:
            self.debug = True

        if self.debug:
            debug_string = " paython.gateways.plugnpay.__init__() -- You're in debug mode"
            print debug_string.center(80, '=')

    def auth(self, amount, credit_card=None, billing_info=None, shipping_info=None):
        """
        Sends charge for authorization only based on amount
        """

        super(PlugnPay, self).set(self.REQUEST_FIELDS['trans_type'], 'authonly')
        super(PlugnPay, self).set(self.REQUEST_FIELDS['trans_mode'], 'auth')
        super(PlugnPay, self).set(self.REQUEST_FIELDS['amount'], amount)

        # validating or building up request
        if not credit_card:
            if self.debug: 
                debug_string = "paython.gateways.plugnpay.auth()  -- No CreditCard object present. You passed in %s " % (credit_card)
                print debug_string

            raise MissingDataError('You did not pass a CreditCard object into the auth method')
        else:
            super(PlugnPay, self).use_credit_card(credit_card)

        if billing_info:
            super(PlugnPay, self).set_billing_info(**billing_info)

        if shipping_info:
            super(PlugnPay, self).set_shipping_info(**shipping_info)

        response, response_time = self.request()
        return self.parse(response, response_time)

    def reauth(self, amount, trans_id):
        """
        Used to settle a transaction at a lower dollar amount.
        """

        super(PlugnPay, self).set(self.REQUEST_FIELDS['trans_mode'], 'reauth')
        super(PlugnPay, self).set(self.REQUEST_FIELDS['trans_id'], trans_id)
        super(PlugnPay, self).set(self.REQUEST_FIELDS['amount'], amount)

        response, response_time = self.request()
        return self.parse(response, response_time)

    def capture(self, amount, credit_card=None, billing_info=None, shipping_info=None):
        """
        Sends transaction for auth + capture (same day settlement) based on amount.
        """

        super(PlugnPay, self).set(self.REQUEST_FIELDS['trans_type'], 'authpostauth')
        super(PlugnPay, self).set(self.REQUEST_FIELDS['trans_mode'], 'auth')
        super(PlugnPay, self).set(self.REQUEST_FIELDS['amount'], amount)

        # validating or building up request
        if not credit_card:
            if self.debug: 
                debug_string = "paython.gateways.plugnpay.capture()  -- No CreditCard object present. You passed in %s " % (credit_card)
                print debug_string

            raise MissingDataError('You did not pass a CreditCard object into the auth method')
        else:
            super(PlugnPay, self).use_credit_card(credit_card)

        if billing_info:
            super(PlugnPay, self).set_billing_info(**billing_info)

        if shipping_info:
            super(PlugnPay, self).set_shipping_info(**shipping_info)

        response, response_time = self.request()
        return self.parse(response, response_time)

    def settle(self, amount, trans_id):
        """
        Sends prior authorization to be settled based on amount & trans_id
        """

        super(PlugnPay, self).set(self.REQUEST_FIELDS['trans_mode'], 'mark')
        super(PlugnPay, self).set(self.REQUEST_FIELDS['trans_id'], trans_id)
        super(PlugnPay, self).set(self.REQUEST_FIELDS['amount'], amount)

        response, response_time = self.request()
        return self.parse(response, response_time)

    def void(self, amount, trans_id):
        """
        Sends a transaction to be voided
        """

        super(PlugnPay, self).set(self.REQUEST_FIELDS['trans_mode'], 'void')
        super(PlugnPay, self).set(self.REQUEST_FIELDS['trans_id'], trans_id)
        super(PlugnPay, self).set(self.REQUEST_FIELDS['amount'], amount)
        super(PlugnPay, self).set('txn-type', 'auth')

        response, response_time = self.request()
        return self.parse(response, response_time)

    def return_transaction(self, amount, trans_id):
        """
        Return funds back to a prior authorization.

        - This cannot be used on transactions over 6 months old
        - This type of return is limited to one use per orderID.
        - Amount returned cannot exceed that of the original auth.
        - Use this mode when returning funds back to the same transaction.
        """

        super(PlugnPay, self).set(self.REQUEST_FIELDS['trans_mode'], 'return')
        super(PlugnPay, self).set(self.REQUEST_FIELDS['trans_id'], trans_id)
        super(PlugnPay, self).set(self.REQUEST_FIELDS['amount'], amount)
        super(PlugnPay, self).set('txn-type', 'auth')

        response, response_time = self.request()
        return self.parse(response, response_time)

    def return_credit(self, amount, trans_id):
        """
        Credits funds, using card info file from a previous transaction.

        - This type of return is NOT linked to the previous transaction's records; instead a new orderID will be associated to each return submitted.
        - This cannot be used on transactions over 6 months old
        - This type of return can be issued for any amount & can be used as often as needed.
        - Use this mode when amount returned exceeds that of the original auth &/or when you want to issue the return to a card already on file.
        - Use this mode when issuing additional returns on a particular transaction. (i.e. use 'return' mode for 1st return, then use 'returnprev' for 2nd, 3rd, 4th, Nth return)
        """

        super(PlugnPay, self).set(self.REQUEST_FIELDS['trans_mode'], 'returnprev')
        super(PlugnPay, self).set(self.REQUEST_FIELDS['trans_id'], trans_id)
        super(PlugnPay, self).set(self.REQUEST_FIELDS['amount'], amount)

        response, response_time = self.request()
        return self.parse(response, response_time)

    def credit(self, amount, credit_card, trans_id=None):
        """
        Credits funds to card info provided

        The optionally submitted `trans_id` overwrites the NEW Credit Transaction.
        If not submitted one will be generated using a date/time string

        - Credits are not associated with any prior authorization; a new orderID will be associated to each credit submitted.
        - Credits can issued for any amount & can be used as often as needed.
        - Use this mode for returning funds on transactions over 6 months old.
        - Use this mode when returning funds to a different card, then what was originally used by the customer.
        """

        super(PlugnPay, self).set(self.REQUEST_FIELDS['trans_mode'], 'newreturn')
        super(PlugnPay, self).set(self.REQUEST_FIELDS['trans_id'], trans_id)
        super(PlugnPay, self).set(self.REQUEST_FIELDS['amount'], amount)

        super(PlugnPay, self).use_credit_card(credit_card)

        response, response_time = self.request()
        return self.parse(response, response_time)

    def query(self, trans_id):
        """
        Ability to query system for credit card transaction information
        """

        super(PlugnPay, self).set(self.REQUEST_FIELDS['trans_mode'], 'query_trans')
        super(PlugnPay, self).set(self.REQUEST_FIELDS['trans_id'], trans_id)

        response, response_time = self.request()
        return self.parse(response, response_time)

    def request(self):
        """
        Makes a request using lib.api.GetGateway.make_request() & move some debugging away from other methods.
        """

        if self.debug:  # I wish I could hide debugging
            debug_string = " paython.gateways.plugnpay.request() -- Attempting request to: "
            print debug_string.center(80, '=')
            debug_string = "\n %s with params: %s" % (self.API_URI, super(PlugnPay, self).params())
            print debug_string

        # make the request
        start = time.time() # timing it
        response = super(PlugnPay, self).make_request(self.API_URI)
        end = time.time() # done timing it
        response_time = '%0.2f' % (end-start)

        if self.debug: # debugging makes code look so nasty
            debug_string = " paython.gateways.plugnpay.request()  -- Request completed in %ss " % response_time
            print debug_string.center(80, '=')

        return response, response_time

    def parse(self, raw_response, response_time):
        """
        On Specific Gateway due differences in response from gateway

        Populates the `response` dict with additional human-readable fields:
        `avs-code-msg`  : AVS code description
        `sresp-msg`     : Simplified Response Code Message (Approved, Declined etc)
        `resp-code-msg` : Gateway Response Code Message
        """

        if self.debug: # debugging is so gross
            debug_string = " paython.gateways.plugnpay.parse() -- Raw response: "
            print debug_string.center(80, '=')
            debug_string = "\n %s" % raw_response
            print debug_string

        #splitting up response into a list so we can map it to Paython generic response
        raw_response = raw_response.split(self.DELIMITER)

        # map key/value keys to `response` dict
        response = {}
        for field in raw_response:
            t = field.split('=')
            response[urllib.unquote(t[0])] = urllib.unquote(t[1]).strip('|').strip()

        # map AVS code to string based on `card-type`
        if response.has_key('avs-code'):
            if response['card-type'] in self.AVS_RESPONSE_KEYS:
                response['avs-code-msg'] = self.AVS_RESPONSE_KEYS[response['card-type']][response['avs-code']]
            else: # default to VISA AVS description
                response['avs-code-msg'] = self.AVS_RESPONSE_KEYS['VISA'][response['avs-code']]

        # simple response code description
        if response.has_key('sresp'):
            response['sresp-msg'] = self.SIMPLE_STATUS_RESPONSE_KEYS[response['sresp']]

        # exact response code description by Merchant Processors
        if response.has_key('resp-code'):
            response['resp-code-msg'] = self.STATUS_RESPONSE_KEYS[response['resp-code']]

        # parse Transaction status
        approved = True if response['success'] == 'yes' else False

        if self.debug: # :& gonna puke
            debug_string = " paython.gateways.plugnpay.parse() -- Response as list: " 
            print debug_string.center(80, '=')
            debug_string = '\n%s' % response
            print debug_string

        return super(PlugnPay, self).standardize(response, self.RESPONSE_KEYS, response_time, approved)

