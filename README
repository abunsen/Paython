== Paython ==

Trying to make it easy to accept payments in Python. So far, we're Paython.

Currently - you can just import the gateway needed from gateways & auth/settle/capture (sale)/void/credit once you instantiate with the proper credentials.

== Supported Gateways ==

* Authorize.net
* Innovative Gateway Solutions (Intuit)
* First Data Global Gateway (formerly Linkpoint?)

== Install Requirements ==

pip install -r requirements.txt

== Run Tests ==

First run:

nosetests -v --with-coverage gateways/*

Then just:

nosetests -v --with-coverage

When initializing a gateway, debug will output request params, xml & response text or xml. test will use the test gateway endpoint, if there is one & will raise an error otherwise (NoTestEndpointError). 
