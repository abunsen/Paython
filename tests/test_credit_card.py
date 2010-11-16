"""
test_credit_card.py - testes our credit card object and validation
"""

from Paython.exceptions import DataValidationError

from nose.tools import assert_equals, assert_false, assert_true, assert_raises with_setup, raises

def setup():
    """setting up the test"""
    global valid_credit_card, invalid_credit_card, invalid_exp_credit_card, invalid_cvv_credit_card

    # create a valid credit card object
    valid_credit_card = CreditCard(
            number="4111111111111111",
            exp_mo="12",
            exp_yr="2099",
    )

    # adding the full name
    valid_credit_card.full_name = "John Doe"

    # create an invaid credit card object
    invalid_credit_card = CreditCard(
            number="4111111111111113",
            exp_mo="12",
            exp_yr="2099",
    )

    # adding the full name
    invalid_credit_card.full_name = "John Doe"

    invalid_exp_credit_card = CreditCard(
            number="4111111111111111",
            exp_mo="06",
            exp_yr="1987",
    )

    # adding the fullname
    invalid_exp_credit_card.full_name = "John Doe"

    invalid_cvv_credit_card = CreditCard(
            number="4111111111111111",
            exp_mo="06",
            exp_yr="1987",
            strict=True,
    )

    # adding the fullname
    invalid_cvv_credit_card.full_name = "John Doe"
    invalid_cvv_credit_card.verification_value = "123456789"

def teardown():
    """teardowning the test"""
    del valid_credit_card
    del invalid_credit_card
    del invalid_exp_credit_card
    del invalid_cvv_credit_card

@with_setup(setup, teardown)
def test_valid():
    """test if a credit card number is luhn valid"""
    # safe check for luhn valid
    assert_true(credit_card.is_valid())

    # check if the credit card is 'visa', this is just double checking
    assert_equals('visa', credit_card.card_type)

    # should not bomb exception
    credit_card._validate()

@with_setup(setup, teardown)
@raises(DataValidationError, 'The credit card number provided does not pass luhn validation')
def test_luhn_invalid():
    """test if a credit card number is luhn invalid"""
    # safe check for valid
    assert_false(invalid_credit_card.is_valid())

    # unsafe check for valid
    invalid_credit_card._validate() # should bomb an exception

@with_setup(setup, teardown)
@raises(DataValidationError, 'The credit card expiration provided is not in the future')
def test_invalid_exp():
    """test invalid expiration date"""
    # safe check for valid
    assert_false(invalid_exp_credit_card.is_valid())

    # bomb the exception
    invalid_exp_credit_card._validate()

@with_setup(setup, teardown)
@raises(DataValidationError, 'The credit card cvv is not valid')
def test_invalid_cvv():
    """test invalid cvv on a credit card"""
    # safe check for valid
    assert_false(invalid_cvv_credit_card.is_valid())

    # bomb the exception
    invalid_cvv_credit_card._validate()
