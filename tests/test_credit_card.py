from Paython.exceptions import DataValidationError
from Paython.lib.cc import CreditCard
from Paython.gateways import FakeGateway

from nose.tools import assert_equals, assert_false, with_setup, raises

def setup():
    """setting up the test"""
    global fake_gateway

    # fake gateway to fake payments
    # (our local shit, basically a mock object, e.g.
    # accepts just valid cc and doesn't make any http requests
    fake_gateway = FakeGateway() # doesn't need username + password

def teardown():
    """teardowning the test"""
    # delete the fake gateway object
    del fake_gateway

@with_setup(setup, teardown)
@raises(DataValidationError)
def test_luhn_invalid():
    """test if a credit card number is luhn invalid"""
    credit_card = CreditCard()
    credit_card.number = "4111111111111113" # invalid credit card
    credit_card.exp = "12/99"
    credit_card.cvv = "123"

    # safe check for luhn valid
    assert_false(credit_card.is_luhn_valid())

    # unsafe check for luhn valid, will bomb an exception
    amount = Decimal("10.10")
    fake_gateway.auth(amount, credit_card)

@with_setup(setup, teardown)
def test_luhn_valid():
    """test if a credit card number is luhn valid"""
    # create a credit card object
    credit_card = CreditCard()
    credit_card.number = "4111111111111111" # valid VISA credit card
    credit_card.exp = "12/99"
    credit_card.cvv = "123"

    # safe check for luhn valid
    assert_false(credit_card.is_luhn_valid())

    # check if the credit card is 'visa', this is just double checking
    assert_equals('visa', credit_card.type)

    # should work
    amount = Decimal("10.00")
    fake_gateway.auth(amount, credit_card)
