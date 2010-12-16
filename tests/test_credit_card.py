from paython.lib.cc import CreditCard
from paython.exceptions import DataValidationError

from nose.tools import assert_equals, assert_false, assert_true, with_setup, raises

def setup():
    """setting up the test"""
    global test_cards
    test_cards = {
            'visa': "4111111111111111",
            'amex': "378282246310005",
            'mc': "5555555555554444",
            'discover': "6011111111111117",
            'diners': "30569309025904"
    }

def teardown():
    """teardowning the test"""
    pass

@with_setup(setup, teardown)
@raises(DataValidationError)
def test_invalid():
    """test if a credit card number is luhn invalid"""
    credit_card = CreditCard(
            number = "4111111111111113", # invalid credit card
            exp_mo = "12",
            exp_yr = "2019",
            first_name = "John",
            last_name = "Doe",
            cvv = "123",
            strict = False
    )

    # checking if the exception fires
    credit_card.validate()

    # safe check for luhn valid
    assert_false(credit_card.is_valid())

@with_setup(setup, teardown)
def test_valid():
    """test if a credit card number is luhn valid"""
    for test_cc_type, test_cc_num in test_cards.items():
        # create a credit card object
        credit_card = CreditCard(
                number = test_cc_num, # invalid credit card
                exp_mo = "12",
                exp_yr = "2019",
                first_name = "John",
                last_name = "Doe",
                cvv = "123",
                strict = False
        )

        # safe check
        assert_true(credit_card.is_valid())

        # check the type
        assert_equals(test_cc_type, credit_card.card_type)
