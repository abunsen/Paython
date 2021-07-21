import os
import hmac
import json
import base64
import decimal
import requests
import datetime
import urlparse
import logging
from hashlib import sha1
from time import gmtime, strftime

from paython.lib.api import PostGateway



def JSONHandler(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    elif isinstance(obj, datetime.datetime):
        return str(obj)

class FirstDataUnauthorizedRequest(Exception):
    pass

logger = logging.getLogger(__name__)

class FirstData(PostGateway):
    """
    FirstData JSON API version 14 support
    https://firstdata.zendesk.com/entries/407571-first-data-global-gateway-e4sm-web-service-api-reference-guide
    """
    GATEWAY_TEST = "api.demo.globalgatewaye4.firstdata.com"
    GATEWAY_LIVE = "api.globalgatewaye4.firstdata.com"
    API_URI = {
                False : GATEWAY_LIVE,
                True :  GATEWAY_TEST
              }
    RESPONSE_FIELDS = {}
    TRANSACTION_TYPES = {
        'purchase': '00',
        'pre_authorization': '01',
        'pre_authorization_completion': '02',
        'refund': '04',
        #'order': '07',
        'void': '13',
        'tagged_pre_authorization_completion': '32',
        'tagged_void': '33',
        'tagged_refund': '34'
    }
    REQUEST_FIELDS = {
        #contact
        'full_name': 'cardholder_name',
        'first_name': None,
        'last_name': None,
        'email': 'client_email',
        'phone': 'phone_number',
        'fax': None,
        #billing
        'address': 'card-address1',
        'address2': 'card-address2',
        'city': 'card-city',
        'state': 'card-state',
        'province': 'card-prov',
        'zipcode': 'card-zip',
        'country': 'card-country',
        'ip': 'client_ip',
        #card
        'number': 'cc_number',
        'exp_date': 'cc_expiry',
        'exp_month': None,
        'exp_year': None,
        'verification_value': 'cc_verification_str2',
        'card_type': 'credit_card_type',
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
        'amount': 'amount',
        'trans_mode': 'mode',
        'trans_type': 'transaction_type',
        'trans_id': 'orderID',
        'alt_trans_id': None,
    }


    def __init__(self, gateway, password, key, secret, **kwargs):
        self.key, self.secret, self.password = str(key), str(secret), str(password)
        self.gateway = str(gateway)
        debug = kwargs.get('debug')
        self.url = self.API_URI.get(debug)
        super(FirstData, self).__init__(self.REQUEST_FIELDS, debug)

    def use_credit_card(self, credit_card):
        """
        Set up credit card info use (if necessary for transaction)
        """
        if hasattr(credit_card, '_exp_yr_style'): # here for gateways that like 2 digit expiration years
            credit_card.exp_year = credit_card.exp_year[-2:]

        for key, value in credit_card.__dict__.items():
            if not key.startswith('_'):
                try:
                    self.set(self.REQUEST_FIELDS[key], value)
                except KeyError:
                    pass # it is okay to fail (on exp_month & exp_year)

        #setting credit card correctly
        if len(credit_card.exp_month) < 2:
            credit_card.exp_month = "0%s" % credit_card.exp_month
        expire_date = '%s%s' % (credit_card.exp_month, credit_card.exp_year[2:])
        #expire date
        self.set('cc_expiry', expire_date)
        del self.REQUEST_DICT[None]


    def purchase(self, amount, cc_obj):
        self.set('gateway_id', self.gateway)
        self.set('password', self.password)
        self.set(self.REQUEST_FIELDS['trans_type'], self.TRANSACTION_TYPES['purchase'])
        self.set(self.REQUEST_FIELDS['amount'], amount)
        self.use_credit_card(cc_obj)
        r = self.request()
        return r

    def auth(self, amount, cc_obj):
        self.set('gateway_id', self.gateway)
        self.set('password', self.password)
        self.set(self.REQUEST_FIELDS['trans_type'], self.TRANSACTION_TYPES['pre_authorization'])
        self.set(self.REQUEST_FIELDS['amount'], amount)
        self.use_credit_card(cc_obj)
        r = self.request()
        return r

    def auth_completion(self, amount, cc_obj, auth_num):
        self.set('gateway_id', self.gateway)
        self.set('password', self.password)
        self.set(self.REQUEST_FIELDS['trans_type'], self.TRANSACTION_TYPES['pre_authorization_completion'])
        self.set('authorization_num', auth_num)
        self.set(self.REQUEST_FIELDS['amount'], amount)
        self.use_credit_card(cc_obj)
        r = self.request()
        return r

        self.set('authorization_num', auth_num)

    def void(self, amount, cc_obj, auth_num):
        self.set('gateway_id', self.gateway)
        self.set('password', self.password)
        self.set(self.REQUEST_FIELDS['trans_type'], self.TRANSACTION_TYPES['void'])
        self.set('authorization_num', auth_num)
        self.set(self.REQUEST_FIELDS['amount'], amount)
        self.use_credit_card(cc_obj)
        r = self.request()
        return r

    def refund(self, amount, cc_obj):
        self.set('gateway_id', self.gateway)
        self.set('password', self.password)
        self.set(self.REQUEST_FIELDS['trans_type'], self.TRANSACTION_TYPES['refund'])
        self.set(self.REQUEST_FIELDS['amount'], amount)
        self.use_credit_card(cc_obj)
        r = self.request()
        return r

    #tagged methods
    def tagged_refund(self, amount, transaction_tag, auth_num):
        self.set('gateway_id', self.gateway)
        self.set('password', self.password)
        self.set(self.REQUEST_FIELDS['trans_type'], self.TRANSACTION_TYPES['tagged_refund'])
        self.set(self.REQUEST_FIELDS['amount'], amount)
        self.set('transaction_tag', transaction_tag)
        self.set('authorization_num', auth_num)
        r = self.request()
        return r

    def tagged_void(self, amount, transaction_tag, auth_num):
        self.set('gateway_id', self.gateway)
        self.set('password', self.password)
        self.set(self.REQUEST_FIELDS['trans_type'], self.TRANSACTION_TYPES['tagged_void'])
        self.set(self.REQUEST_FIELDS['amount'], amount)
        self.set('transaction_tag', transaction_tag)
        self.set('authorization_num', auth_num)
        r = self.request()
        return r

    def tagged_pre_authorization_completion(self, amount, transaction_tag, auth_num):
        self.set('gateway_id', self.gateway)
        self.set('password', self.password)
        self.set(self.REQUEST_FIELDS['trans_type'], self.TRANSACTION_TYPES['tagged_pre_authorization_completion'])
        self.set(self.REQUEST_FIELDS['amount'], amount)
        self.set('transaction_tag', transaction_tag)
        self.set('authorization_num', auth_num)
        r = self.request()
        return r

    def request(self, retry_on_bmc=1):
        """Send the transaction out to First Data
        """

        self._retry_on_bmc = retry_on_bmc
        assert type(self.debug) is bool, "Invalid test value, must be type boolean"

        gge4_date = strftime("%Y-%m-%dT%H:%M:%S", gmtime()) + 'Z'
        transaction_body = json.dumps(self.REQUEST_DICT, default=JSONHandler)
        content_digest = sha1(transaction_body).hexdigest()
        headers = {'Content-Type': "application/json",
                   'Accept': "application/json",
                   'X-GGe4-Content-SHA1': content_digest,
                   'X-GGe4-Date': gge4_date,
                   'Authorization': 'GGE4_API ' + self.key + ':' + base64.b64encode(hmac.new(self.secret, "POST\napplication/json\n"+content_digest+"\n"+gge4_date+"\n/transaction/v14", sha1).digest())}

        r = requests.post(("https://" + self.url + "/transaction/v14"),
                            timeout=20,
                            verify=not self.debug,
                            data=transaction_body,
                            headers=headers)
        if self.debug:
            debug_str = "response code: %s" % r.status_code
            logger.debug(debug_str.center(80, '='))
        return self.parse(r)

    def parse(self, response):
        response = response.text
        if self.debug:
            logger.debug(response)
        if type(self._retry_on_bmc) is int and 0 < self._retry_on_bmc < 4 and response == "Unauthorized Request. Bad or missing credentials.":
            """When FDs servers return "Unauthorized Request. Bad or missing credentials."
            which happened quite often for ABSOLUTLY no reason. We will try the request again.
            3 attempts will be made if this error occurs.
            I have contacted their support about this issue...sometime ago.
            """
            if self.debug:
                logger.debug(json.dumps(dict(attempt=self._retry_on_bmc, source="First Data Unauthorized Request")))

            raise FirstDataUnauthorizedRequest()

        else:
            try:
                json_response = json.loads(response)
                return json_response
            except:
                """FirstData sometimes sends back a http-args not a json argument...ugh.
                """
                try:
                    urlargs = dict(urlparse.parse_qsl(response))
                    if len(urlargs)==0:
                        raise ValueError("Move to text...")
                    else:
                        return urlargs
                except:
                    """FirstData also sends back string errors.
                    """
                    # make my own FirstData Error
                    error = {"transaction_approved":0,"bank_message":response,"amount":self.REQUEST_DICT.get('amount',0),"fraud_suspected":None,"success":False,"reference_3":None,"cvd_presence_ind":0,"bank_resp_code":None,"partial_redemption":0,"card_cost":None,"exact_message":response,"logon_message":None,"secure_auth_result":None,"payer_id":None,"transaction_type":self.REQUEST_DICT.get('transaction_type'),"cc_verification_str2":None,"ecommerce_flag":None,"reference_no":self.REQUEST_DICT.get('reference_no'),"cavv":None,"previous_balance":None,"error_description":None,"tax2_number":None,"exact_resp_code":None,"secure_auth_required":None,"amount_requested":None,"client_email":None,"cc_verification_str1":None,"language":None}
                    return error
