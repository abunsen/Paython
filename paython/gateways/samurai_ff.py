import time

from paython.gateways.core import Gateway
from paython.exceptions import *

try:
    import samurai.config as config
    from samurai.payment_method import PaymentMethod
    from samurai.processor import Processor
    from samurai.transaction import Transaction
except ImportError:
    raise Exception('Samurai library not found, please install requirements.txt')

class Samurai(Gateway):
    """TODO needs docstring"""
    VERSION = 'v1'

    REQUEST_FIELDS = {
        'first_name':'first_name',
        'last_name':'last_name',
        'address':'address_1',
        'city':'city',
        'state':'state',
        'zipcode':'zip'
    }

    RESPONSE_KEYS = {
        'transaction_token':'trans_id',
        'transaction_type':'trans_type',
        'reference_id':'alt_trans_id',
        'amount':'amount'
    }

    def __init__(self, merchant_key=None, password=None, processor=None, debug=False):
        """
        setting up object so we can run 2 different ways (live & debug)

        we have username and api_key because other gateways use "username" 
        and we want to make it simple to change out gateways ;)
        """
        config.merchant_key = merchant_key
        config.merchant_password = password
        config.processor_token = processor

        # passing fields to bubble up to Base Class
        super(Samurai, self).__init__(set_method=self.set, translations=self.REQUEST_FIELDS, debug=debug)

        if debug:
            self.debug = True
            debug_string = " paython.gateways.samurai_ff.__init__() -- You're in debug mode"
            print debug_string.center(80, '=')

    def set(self, key, value):
        """
        Does not serve a purpose other than to let us inherit
        from core.Gateway with no problems
        """
        pass

    def translate(self, info):
        """
        Translates the data for billing_info
        """
        new_dict = dict()
        for k, v in info.items():
            try:
                new_dict[self.REQUEST_FIELDS[k]] = v
            except KeyError:
                pass
        return new_dict

    def charge_setup(self, card, billing_info):
        """
        standard setup, used for charges
        """
        billing_info = self.translate(billing_info)

        # use the card + extra data- send it to samurai for storage and tokenization
        card._exp_yr_style = True
        super(Samurai, self).use_credit_card(card)
        pm = PaymentMethod.create(
                    card.number, 
                    card.verification_value, 
                    card.exp_month, card.exp_year, **billing_info)

        if self.debug:
            debug_string = " paython.gateways.samurai_ff.charge_setup() -- response on setting pm"
            print debug_string.center(80, '=')
            print dir(pm)

        if pm.errors:
            raise DataValidationError('Invalid Card Data: %s' % pm.errors[pm.error_messages[0]['context']][0])

        return pm.payment_method_token

    def auth(self, amount, credit_card=None, billing_info=None, shipping_info=None):
        # set up the card for charging, obviously
        card_token = self.charge_setup(credit_card, billing_info)
        # start the timer
        start = time.time()
        # send it over for processing
        response = Processor.authorize(card_token, amount)
        # measure time
        end = time.time() # done timing it
        response_time = '%0.2f' % (end-start)
        # return parsed response
        return self.parse(response, response_time)

    def settle(self, amount, trans_id):
        txn = Transaction.find(trans_id)
        if txn.errors:
            raise GatewayError('Problem fetching transaction: %s' % txn.errors[txn.error_messages[0]['context']][0])
        else:
            # start the timer
            start = time.time()
            response = txn.capture(amount)
            # measure time
            end = time.time() # done timing it
            response_time = '%0.2f' % (end-start)
            # return parsed response
            return self.parse(response, response_time)
            
    def capture(self, amount, credit_card=None, billing_info=None, shipping_info=None):
        # set up the card for charging, obviously
        card_token = self.charge_setup(credit_card, billing_info)
        # start the timer
        start = time.time()
        # send it over for processing
        response = Processor.purchase(card_token, amount)
        # measure time
        end = time.time() # done timing it
        response_time = '%0.2f' % (end-start)
        # return parsed response
        return self.parse(response, response_time)

    def void(self, trans_id):
        txn = Transaction.find(trans_id)
        if txn.errors:
            raise GatewayError('Problem fetching transaction: %s' % txn.errors[txn.error_messages[0]['context']][0])
        else:
            # start the timer
            start = time.time()
            response = txn.void()
            # measure time
            end = time.time() # done timing it
            response_time = '%0.2f' % (end-start)
            # return parsed response
            return self.parse(response, response_time)

    def credit(self, amount, trans_id):
        txn = Transaction.find(trans_id)
        if txn.errors:
            raise GatewayError('Problem fetching transaction: %s' % txn.errors[txn.error_messages[0]['context']][0])
        else:
            # start the timer
            start = time.time()
            response = txn.reverse(amount)
            # measure time
            end = time.time() # done timing it
            response_time = '%0.2f' % (end-start)
            # return parsed response
            return self.parse(response, response_time)

    def parse(self, response, response_time):
        """
        Make sure we translate the stuff not in self.RESPONSE_KEYS, like:
        cvv_response
        avs_response
        response_text
        """
        resp = response.__dict__
        rd = super(Samurai, self).standardize(resp, self.RESPONSE_KEYS, response_time, resp['success'])
        
        # now try to update the other stuff
        if response.errors:
            rd['response_text'] = resp['errors'][resp['error_messages'][0]['context']][0]
            rd['cvv_response'] = resp['processor_response'].get('cvv_result_code')
            rd['avs_response'] = resp['processor_response'].get('avs_result_code')

        return rd