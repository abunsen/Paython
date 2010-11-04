import random

from paython.lib.api import XMLGatewayInterface, GatewayError

class FirstDataError(Exception):
    """Useful if you want to raise an exception on a failed call"""
    def __init__(self, val):
        self.value = val
    def __str__(self):
        return self.value

class FirstData(XMLGatewayInterface):
    """ Execute First Data Gateway API calls through a simple interface

    This wrapper is used to place orders via API. XML Meta:

        order
        
            merchantinfo
                configfile (store number)
                keyfile (path to pem file) - potentially not required
                host (as spec'd in welcome email) - potentially not required
                port (??) - potentially not required
            
            orderoptions
                ordertype
                result (Live, Good, Decline, Duplicate)
            
            payment
                chargetotal
            
            creditcard
                cardnumber
                cardexpmonth (2)
                cardexpyear (2)
                cvmvalue
                cvmindicator
            
            billing
                name
                address1
                city
                state
                zip
                country
                phone
                addrnum
    """

    API_URI = {
        'order' : 'LSGSXML',
    }

    API_BASE = {
        'order' : 'secure.linkpt.net', # https
    }
    
    REQ_CC_DATA = ['cardnumber', 'cardexpmonth', 'cardexpyear', 'cvmvalue']
    REQ_TRANS_DATA = ['name','address1', 'city', 'state', 'zip', 'phone', 'addrnum']

    def __init__(self, api_user, debug=False, test=False):
        self.api_user = api_user
        self.test = test
        ssl_connect_params = {'port':'1129', 'key_file':'../keys/firstdata.pem-file', 'cert_file':'../keys/firstdata.pem-file'}
        super(FirstData, self).__init__(self.API_BASE['order'], ssl=True, debug=debug, special_params=ssl_connect_params)

    def auth(self, amount=None, trans_data=None, cc_data=None):
        """
        Sends charge for authorization based on amount
        """
        response_dict = {}

        #validation
        if not all([trans_data.get(key) for key in self.REQ_TRANS_DATA]): response_dict['error'] = 'missing transaction data'
        if not all([cc_data.get(key) for key in self.REQ_CC_DATA]): response_dict['error'] = 'missing transaction & credit card data'

        if 'error' in response_dict: return response_dict

        #setting order options 
        super(FirstData, self).set('order/orderoptions/ordertype', 'Preauth')

        #setting payment total
        super(FirstData, self).set('order/payment/chargetotal', amount)

        #setting cc info
        for item_key in cc_data.keys():
            super(FirstData, self).set('order/creditcard/%s' % item_key, cc_data[item_key])

        #setting customer info - 2 different loops because of the parent noe
        for item_key in trans_data.keys():
            super(FirstData, self).set('order/billing/%s' % item_key, trans_data[item_key])

        response_dict = self.post()

        return response_dict

    def settle(self, amount=None, trans_id=None):
        """
        Sends charge for sale capture based on amount
        """
        response_dict = {}

        #basic validation
        if not amount or not trans_id: return {'error': 'missing an amount to settle or trans_id - original r_ordernum'}

        #setting order options 
        super(FirstData, self).set('order/orderoptions/ordertype', 'Postauth')

        #setting payment total
        super(FirstData, self).set('order/payment/chargetotal', amount)

        #setting the original order number / id
        super(FirstData, self).set('order/transactiondetails/oid', trans_id)

        response_dict = self.post()

        return response_dict

    def sale(self, amount=None, trans_data=None, cc_data=None):
        """
        Sends charge for sale capture based on amount
        """
        response_dict = {}

        #validation
        if not all([trans_data.get(key) for key in self.REQ_TRANS_DATA]): response_dict['error'] = 'missing transaction data'
        if not all([cc_data.get(key) for key in self.REQ_CC_DATA]): response_dict['error'] = 'missing transaction & credit card data'

        if 'error' in response_dict: return response_dict

        #setting order options 
        super(FirstData, self).set('order/orderoptions/ordertype', 'Sale')

        #setting payment total
        super(FirstData, self).set('order/payment/chargetotal', amount)

        #setting cc info
        for item_key in cc_data.keys():
            super(FirstData, self).set('order/creditcard/%s' % item_key, cc_data[item_key])

        #setting customer info - 2 different loops because of the parent noe
        for item_key in trans_data.keys():
            super(FirstData, self).set('order/billing/%s' % item_key, trans_data[item_key])

        response_dict = self.post()

        return response_dict

    def credit(self, amount=None, trans_id=None):
        """
        Send a transaction to be refunded (partially or fully)
        """
        response_dict = {}

        #basic validation
        if not amount or not trans_id: return {'error': 'missing an amount or trans_id'}

        #setting order options 
        super(FirstData, self).set('order/orderoptions/ordertype', 'Credit')

        #setting the original order number / id
        super(FirstData, self).set('order/transactiondetails/oid', trans_id)

        #setting refund total
        super(FirstData, self).set('order/payment/chargetotal', amount)

        response_dict = self.post()

        return response_dict

    def void(self, trans_id=None):
        """
        Send a SALE (only works for sales) transaction to be voided (in full) that was initially sent for captuer the same day
        """
        response_dict = {}

        #basic validation
        if not trans_id: return {'error': 'missing trans_id - the original r_ordernum'}

        #setting order options 
        super(FirstData, self).set('order/orderoptions/ordertype', 'Void')

        #setting the original order number / id
        super(FirstData, self).set('order/transactiondetails/oid', trans_id)

        response_dict = self.post()

        return response_dict

    def post(self):
        xml_path_root = self.doc.childNodes
        if not xml_path_root: return
        xml_path_root = xml_path_root[0].tagName

        # woot woot
        uri = self.API_URI[xml_path_root]

        # set API store id creds
        super(FirstData, self).set('%s/merchantinfo/configfile' % xml_path_root, self.api_user)
        # set Other required fields that are static
        super(FirstData, self).set('order/creditcard/cvmindicator', 'provided')
        super(FirstData, self).set('order/billing/country', 'US')
        
        if self.test:
            super(FirstData, self).set('order/orderoptions/result', 'Good')
        else:
            super(FirstData, self).set('order/orderoptions/result', 'Live')
        
        # now get to posting
        resp = super(FirstData, self).post(uri)

        # raise exception if needed - why did I put this here?
        resp_error = resp[resp.keys()[0]].has_key('Exception')
        if resp_error:
            err_str = resp[resp.keys()[0]]['Exception']
            raise GatewayError(err_str)

        return resp
