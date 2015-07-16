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


first_data = gateways.FirstData(gateway="",
                                password="",
                                key="",
                                secret='',
                                debug=True
                                )

mycard = {
    'full_name': 'Customer',
    'number': '4111111111111111',
    'cvv': '904',
    'exp_mo': '12',
    'exp_yr': '2016'
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

#print first_data.purchase('410.00', cc_obj )
#print first_data.void('410.00', cc_obj, 'ET107394')
#print first_data.auth('0.01', cc_obj)
#print first_data.auth_completion('0.01', cc_obj, 'ET159026')
print first_data.tagged_refund('410.00', '34312757', 'ET180377')
#print first_data.tagged_pre_authorization_completion('0.01', '34328111', 'ET138075')
#print first_data.tagged_void('410.00', '34333001', 'ET186692')
