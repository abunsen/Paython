"""authorize_net.py - Authorize.Net example"""

try:
    from paython import api, gateways, CreditCard
except ImportError:
    # adding paython to the path
    # to run this without installing the library
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

    # trying again
    from paython import api, gateways, CreditCard

api = gateways.AuthorizeNet(username='test',
                            password='test',
                            test=True)

mycard = {
    'first_name': 'auston',
    'last_name': 'bunsen',
    'number': '4111111111111111',
    'exp_mo': '12',
    'exp_yr': '2012'
}

cc_obj = CreditCard(**mycard)

billing = {
    'address': '7519 NW 88th Terrace',
    'city': 'Tamarac',
    'state': 'FL',
    'zipcode': '33321',
    'phone': '9546703289',
    'email': 'auston@gmail.com'
}

api.auth('0.22', cc_obj, billing)
api.void('2155779779')
