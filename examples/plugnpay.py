"""plugnpay.py - PlugnPay.com example"""

try:
    from paython import gateways, CreditCard
except ImportError:
    # adding paython to the path
    # to run this without installing the library
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

    # trying again
    from paython import gateways, CreditCard

# enter your `email` to receive gateway notifications
api = gateways.PlugnPay(username='pnpdemo', password='', email='')

mycard = {
    'first_name': 'auston',
    'last_name': 'bunsen',
    'number': '41111111111111',
    'exp_mo': '12',
    'exp_yr': '2012'
}

cc_obj = CreditCard(**mycard)

billing = {
    'address': '7519 NW 88th Terrace',
    'city': 'Tamarac',
    'state': 'FL',
    'zipcode': '33321',
    'country' : 'US',
    'phone': '3053333333',
    'email': 'manuel@140.am'
}

print '-----------------------------'

trans = api.capture('1.0', cc_obj, billing)
print trans
