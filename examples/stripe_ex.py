from paython import api, gateways, CreditCard

api = gateways.Stripe(username="vtUQeOtUnYr7PGCLQ96Ul4zqpDUO4sOE")#, debug=True)

mycard = {
    'first_name': 'auston',
    'last_name': 'bunsen',
    'number': '4242424242424242',
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

api.capture('0.22', cc_obj, billing)
ex = api.capture('10.22', cc_obj, billing)
api.credit('5.55', ex['trans_id'])
api.void('2155779779')