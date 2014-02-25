from datetime import datetime
from dateutil.relativedelta import relativedelta

from paython.lib.echeck import ECheck
from paython.exceptions import DataValidationError

from nose.tools import assert_equals, assert_false, assert_true, with_setup, raises

# Initialize globals here so that pyflakes doesn't freak out about them.
TEST_ECHECKS = {}
TEST_ABAS = {}

def setup():
    """setting up the test"""

    global TEST_CARDS
    global TEST_ABAS
    
    TEST_ABAS = [ "123456789123", ]

def teardown():
    """teardowning the test"""
    pass

@with_setup(setup, teardown)
@raises(DataValidationError)
def test_invalid():
    """test if a ABA Routing Number is invalid"""
    echeck = ECheck(
            aba_code = "011000014", # invalid ABA CODE
            acct_num = "123456789123",
            acct_type = "Checking",
            bank_name = "bank1",
            first_name = "John",
            last_name = "Doe",
    )

    # safe check for validity
    assert_false(echeck.is_valid())

    # checking if the exception fires
    echeck.validate()

@with_setup(setup, teardown)
def test_valid():
    """test if a ABA routing number is valid"""
    for test_echeck_aba in TEST_ABAS:
        # create a credit card object
        echeck = ECheck(
            aba_code = "011000015",
            acct_num = "123456789123",
            acct_type = "Checking",
            bank_name = "bank1",
            first_name = "John",
            last_name = "Doe",
        )

        # safe check
        assert_true(echeck.is_valid())

