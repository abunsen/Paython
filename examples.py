# ==== Authorize.Net ==== #

from Paython import *
api = gateways.AuthorizeNet(username='test', password='test', test=True)
mycard = {'first_name':'auston', 'last_name':'bunsen', 'number':'4111111111111111', 'exp_mo':'12', 'exp_yr':'2012'}
cc_obj = CreditCard(**mycard)
billing = {'address':'7519 NW 88th Terrace', 'city':'Tamarac', 'state':'FL', 'zipcode':'33321', 'phone':'9546703289', 'email':'auston@gmail.com'}
api.auth('0.22', cc_obj, billing)
api.void('2155779779')

# ==== Innovative GW ==== #

from Paython import *
api = gateways.InnovativeGW(username='test', password='test', debug=True)
mycard = {'full_name':'auston bunsen', 'number':'4111111111111111', 'cvv':'771', 'exp_mo':'12', 'exp_yr':'2012'}
cc_obj = CreditCard(**mycard)
billing = {'address':'7519 NW 88th Terrace', 'city':'Tamarac', 'state':'FL', 'zipcode':'33321', 'country':'US', 'phone':'9546703289', 'email':'auston@gmail.com'}
api.auth('1.22', cc_obj, billing)

# ==== FirstData legacy ==== #

from Paython import *
pem = '/Path/to/your/yourkey.pem'
api = gateways.FirstDataLegacy(username='1329411', key_file=pem, cert_file=pem, debug=True, test=True)
mycard = {'full_name':'auston bunsen', 'number':'5555555555554444', 'cvv':'904', 'exp_mo':'12', 'exp_yr':'2012'}
cc_obj = CreditCard(**mycard)
billing = dict(address='7519 NW 88th Terrace', city='Tamarac', state='FL', zipcode='33321', country='US', phone='9547212241', email='auston@gmail.com')
api.auth('0.01', cc_obj, billing)

# ==== FirstData SOAP ==== #