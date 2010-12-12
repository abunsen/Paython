"""innovative_gw.py - Innovative GW example"""

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

api = gateways.InnovativeGW(username='test',
                            password='test',
                            debug=True)

mycard = {
    'full_name': 'auston bunsen',
    'number': '4111111111111111',
    'cvv': '771',
    'exp_mo': '12',
    'exp_yr': '2012'
}

cc_obj = CreditCard(**mycard)

billing = {
    'address': '7519 NW 88th Terrace',
    'city': 'Tamarac',
    'state': 'FL',
    'zipcode': '33321',
    'country': 'US',
    'phone': '9546703289',
    'email': 'auston@gmail.com'
}

api.auth('1.22', cc_obj, billing)
