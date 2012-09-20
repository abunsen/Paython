import time

try:
    import stripe
except ImportError:
    raise Exception('Stripe library not found, please install requirements.txt')

class Stripe(object):
    """TODO needs docstring"""
    VERSION = 'v1'

    RESPONSE_KEYS = {
        'id':'trans_id',
        'amount':'amount',
        'cvv_response':'cvc_check',
        'avs_response':'address_line1_check',   
    }
    debug = False
    test = False
    stripe_api = stripe

    def __init__(self, username=None, api_key=None, debug=False):
        """
        setting up object so we can run 2 different ways (live & debug)

        we have username and api_key because other gateways use "username" 
        and we want to make it simple to change out gateways ;)
        """
        self.stripe_api.api_key = username or api_key

        if debug:
            self.debug = True
            debug_string = " paython.gateways.stripe.__init__() -- You're in debug mode"
            print debug_string.center(80, '=')

    def auth(self, amount, credit_card=None, billing_info=None, shipping_info=None):
        """
        Not implemented because stripe does not support authorizations:
        https://answers.stripe.com/questions/can-i-authorize-transactions-first-then-charge-the-customer-after-service-is-comp
        """
        raise NotImplementedError('Stripe does not support auth or settlement. Try capture().')

    def settle(self, amount, trans_id):
        """
        Not implemented because stripe does not support auth/settle:
        https://answers.stripe.com/questions/can-i-authorize-transactions-first-then-charge-the-customer-after-service-is-comp
        """
        raise NotImplementedError('Stripe does not support auth or settlement. Try capture().')

    def capture(self, amount, credit_card=None, billing_info=None, shipping_info=None):
        if self.debug: # debugging is so gross
            debug_string = " paython.gateways.stripe.parse() -- Sending charge "
            print debug_string.center(80, '=')

        amount = int(float(amount)*100) # then change the amount to how stripe likes it

        start = time.time() # timing it
        try:
            response = self.stripe_api.Charge.create(
                amount=amount,
                currency="usd",
                card={
                    "name":credit_card.full_name,
                    "number": credit_card.number,
                    "exp_month": credit_card.exp_month,
                    "exp_year": credit_card.exp_year,
                    "cvc": credit_card.verification_value if credit_card.verification_value else None,
                    "address_line1":billing_info.get('address'),
                    "address_line2":billing_info.get('address2'),
                    "address_zip":billing_info.get('zipcode'),
                    "address_state":billing_info.get('state')
                },
            )
        except stripe.InvalidRequestError, e:
            response = {'failure_message':'Invalid Request: %s' % e}
            end = time.time() # done timing it
            response_time = '%0.2f' % (end-start)
        except stripe.CardError, e:
            response = {'failure_message':'Card Error: %s' % e}
            end = time.time() # done timing it
            response_time = '%0.2f' % (end-start)
        else:
            end = time.time() # done timing it
            response_time = '%0.2f' % (end-start)

        return self.parse(response, response_time)

    def void(self, trans_id):
        """
        Not implemented because Stripe does not support transaction voiding
        """
        raise NotImplementedError('Stripe does not support transaction voiding. Try credit().')

    def credit(self, amount, trans_id):
        if self.debug: # debugging is so gross
            debug_string = " paython.gateways.stripe.parse() -- Sending credit "
            print debug_string.center(80, '=')

        amount = int(float(amount)*100)
        start = time.time() # timing it
        try:
            ch = self.stripe_api.Charge.retrieve(trans_id)
            response = ch.refund(amount=amount)
        except Exception, e:
            response = {'failure_message':'Unable to refund: %s' % e}
            end = time.time() # done timing it
            response_time = '%0.2f' % (end-start)
        else:
            end = time.time() # done timing it
            response_time = '%0.2f' % (end-start)

        return self.parse(response, response_time)

    def parse(self, response, response_time):
        """
        turn the response into a dict and attach these things:
        response_text
        response_time
        trans_type
        approved
        cvv_response
        avs_response

        before returning the dict
        """
        if hasattr(response, 'to_dict'):
            response = response.to_dict()

        if self.debug: # debugging is so gross
            debug_string = " paython.gateways.stripe.parse() -- Dict response: "
            print debug_string.center(80, '=')
            debug_string = "\n %s" % response
            print debug_string
        
        new_response = {}

        # alright now lets stuff some info in here
        new_response['response_time'] = response_time
        # determining success
        new_response['response_text'] = response['failure_message'] or 'success'
        new_response['approved'] = True if not response['failure_message'] else False
        # trans type ;)
        new_response['trans_type'] = 'credit' if response.get('amount_refunded') > 0 else 'capture'

        for key in self.RESPONSE_KEYS.keys():
            if response.get(key):
                if key == 'amount':
                    response[key] = '%.2f' % (float(response[key])/float(100))

                new_response[self.RESPONSE_KEYS[key]] = response[key]
        return new_response