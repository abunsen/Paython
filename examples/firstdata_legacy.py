"""firstdata.py - Firstdata legacy example"""

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

pem = '/Path/to/your/yourkey.pem'

api = gateways.FirstDataLegacy(username='1329411',
                               key_file=pem,
                               cert_file=pem,
                               debug=True,
                               test=True)

mycard = {
    'full_name': 'auston bunsen',
    'number': '5555555555554444',
    'cvv': '904',
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
    'phone': '9547212241',
    'email': 'auston@gmail.com'
}

api.auth('0.01', cc_obj, billing)
