from paython import api, gateways, CreditCard

api = gateways.Samurai(
	merchant_key='202fc9c52312295d8ab93048', 
	password='f5b06686bc8d0625560f7a6d', 
	processor='df52fa67def1a3e85a0affce'
)

mycard = {
    'first_name': 'John',
    'last_name': 'Doe',
    'number': '4111111111111111',
    'exp_mo': '12',
    'exp_yr': '2012',
    'cvv':'111',
    'strict': True
}

cc_obj = CreditCard(**mycard)

billing = {
    'address': '1000 1st Av',
    'city': 'Chicago',
    'state': 'IL',
    'zipcode': '10101',
    'phone': '9546703289',
    'email': 'auston@gmail.com'
}

authorization = api.auth('1.00', cc_obj, billing)
print authorization
print api.void(authorization['alt_trans_id'])