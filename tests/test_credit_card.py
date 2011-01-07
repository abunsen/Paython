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

    # safe check for luhn valid
    assert_false(credit_card.is_valid())

    # checking if the exception fires
    credit_card.validate()

@with_setup(setup, teardown)
@raises(DataValidationError)
def test_invalid():
    """test if a credit card number is luhn invalid"""
    credit_card = CreditCard(
            number = "411111111111111a", # invalid credit card
            exp_mo = "12",
            exp_yr = "2019",
            first_name = "John",
            last_name = "Doe",
            cvv = "123",
            strict = False
    )

    # safe check for luhn valid
    assert_false(credit_card.is_valid())

    # checking if the exception fires
    credit_card.validate()

@with_setup(setup, teardown)
@raises(DataValidationError)
def test_expired_credit_card():
    """test if a credit card number is expired"""
    credit_card = CreditCard(
            number = "4111111111111111",
            exp_mo = "12",
            exp_yr = "1990", # old ass credit card
            first_name = "John",
            last_name = "Doe",
            cvv = "123",
            strict = False
    )

    # safe check for luhn valid
    assert_false(credit_card.is_valid())

    # checking if the exception fires
    credit_card.validate()

@with_setup(setup, teardown)
@raises(DataValidationError)
def test_invalid_cvv():
    """test if a credit card number has an invalid cvv"""
    credit_card = CreditCard(
            number = "4111111111111111",
            exp_mo = "12",
            exp_yr = "2018",
            first_name = "John",
            last_name = "Doe",
            cvv = "1", # invalid cvv
            strict = True
    )

    # safe check for luhn valid
    assert_false(credit_card.is_valid())

    # checking if the exception fires
    credit_card.validate()

@with_setup(setup, teardown)
def test_valid():
    """test if a credit card number is luhn valid"""
    for test_cc_type, test_cc_num in test_cards.items():
        # create a credit card object
        credit_card = CreditCard(
                number = test_cc_num, # valid credit card
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

@with_setup(setup, teardown)
def test_to_string():
    """test if a credit card outputs the right to str value"""
    credit_card = CreditCard(
            number = '4111111111111111',
            exp_mo = '02',
            exp_yr = '2012',
            first_name = 'John',
            last_name = 'Doe',
            cvv = '911',
            strict = False
    )

    # safe check
    assert_true(credit_card.is_valid())

    # checking if our str() method (or repr()) is ok
    final_str = '<CreditCard -- John Doe, visa, ************1111, expires: 02/2012>'
    assert_equals(str(credit_card), final_str)

@with_setup(setup, teardown)
def test_full_name():
    """testing full_name support"""
    credit_card = CreditCard(
            number = '4111111111111111',
            exp_mo = '02',
            exp_yr = '2012',
            full_name = 'John Doe',
            cvv = '911',
            strict = False
    )

    # safe check
    assert_true(credit_card.is_valid())

    # checking if our str() method (or repr()) is ok
    final_str = '<CreditCard -- John Doe, visa, ************1111, expires: 02/2012>'
    assert_equals(str(credit_card), final_str)

@with_setup(setup, teardown)
def test_exp_styled():
    """testing support for 2 digits expiracy year"""
    credit_card = CreditCard(
            number = '4111111111111111',
            exp_mo = '02',
            exp_yr = '2012',
            full_name = 'John Doe',
            cvv = '911',
            strict = False
    )

    credit_card._exp_yr_style = True

    # safe check
    assert_true(credit_card.is_valid())

    # checking if our str() method (or repr()) is ok
    final_str = '<CreditCard -- John Doe, visa, ************1111, expires: 02/2012 --extra: 12>'
    assert_equals(str(credit_card), final_str)
