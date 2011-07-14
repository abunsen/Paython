Paython
=========

Trying to make it easy to accept payments in Python. So far, we're Paython.

Currently - you can just import the gateway needed from gateways & auth/settle/capture (sale)/void/credit once you instantiate with the proper credentials.

Supported Gateways
==================

* Authorize.net
* Innovative Gateway Solutions (Intuit)
* First Data Global Gateway (formerly Linkpoint?)
* PlugnPay

Usage
===========================

https://github.com/abunsen/Paython/wiki/Usage

Install Requirements
===========================

You need pip::

    pip install -r requirements.txt

Run Tests
=========

Just run::

    nosetests

Or with stats::

    nosetests --quiet --with-coverage --cover-package paython

When initializing a gateway, debug will output request params, xml & response text or xml. test will use the test gateway endpoint, if there is one & will raise an error otherwise (NoTestEndpointError). 
