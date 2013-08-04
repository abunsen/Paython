Paython
=========

[![Build Status](https://travis-ci.org/abunsen/Paython.png)](https://travis-ci.org/abunsen/Paython)

Trying to make it easy to accept payments in Python. So far, we're Paython - a library in python for payment gateways like Stripe, ePay, Authorize.net, PlugNPay, First Data & more.

Currently - you can just import the gateway needed from gateways & auth/settle/capture (sale)/void/credit once you instantiate with the proper credentials.

*IMPORTANT:* If you fork & make a cool or useful change, we'd really love it if you wrote some associated tests & issued a pull request that way we can keep this repo up to date ;)

Supported Gateways
==================

* Stripe
* Authorize.net
* Innovative Gateway Solutions (Intuit)
* First Data Global Gateway (formerly Linkpoint?)
* PlugnPay
* Samurai
* ePay (untested)

Usage
===========================
It's super simple to start:

Importing what you need

```py
from paython import CreditCard, AuthorizeNet
```

Setting up a credit card

```py
credit_card = CreditCard(
    number = '4111111111111111',
    exp_mo = '02',
    exp_yr = '2012',
    first_name = 'John',
    last_name = 'Doe',
    cvv = '911',
    strict = False
)
```

Checking to see if it's valid

```py
 if not credit_card.is_valid(): return 'houston, we have a problem' # checks card number + expiration date
```

Setting up customer data to charge, not all fields are required.

```py
customer_data = dict(
    address='123 Main St', 
    address2='Apt 1', 
    city='Pleasantville', 
    state='IA', 
    zipcode='54321', 
    country='US', 
    phone='654-369-9589', 
    email='john@localwoodshop.com', 
    ip='127.0.0.1')
```

Trying to authorize against gateway, options include debug output or test credentials

```py
api = AuthorizeNet(username='test', password='testpassword', debug=True, test=True)
gateway_response = api.auth(amount='0.05', credit_card=credit_card, billing_info=customer_data, shipping_info=None)
```

Keep in mind, if you authorize, you need to settle 

```py
api = AuthorizeNet(username='test', password='testpassword', debug=True, test=True)
gateway_response = api.settle(amount='0.05', trans_id='2156729380')
```

OR, you can capture instead

```py
api = AuthorizeNet(username='test', password='testpassword', debug=True, test=True)
gateway_response = api.capture(amount='0.05', credit_card=credit_card, billing_info=customer_data, shipping_info=None)
```


This is a typical paython response.

```py
    gateway_response = {
        'response_text': 'This transaction has been approved.',
        'cvv_response': 'P',
        'response_code': '1',
        'trans_type': 'auth_only',
        'amount': '0.05',
        'avs_response': 'Y',
        'response_reason_code': '1',
        'trans_id': '2156729380',
        'alt_trans_id': '',
        'auth_code': 'IL2UW7',
        'approved': True,
        'response_time': '0.55'
    }
```

Install
=======

You can use pip to install Paython::

    pip install paython

Run Tests
=========

Just run::

    nosetests

Or with stats::

    nosetests --quiet --with-coverage --cover-package paython

When initializing a gateway, debug will output request params, xml & response text or xml. test will use the test gateway endpoint, if there is one & will raise an error otherwise (NoTestEndpointError). 
