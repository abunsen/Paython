"""test_exceptions.py: testing exceptions just raising them and testing them"""
from paython.exceptions import DataValidationError, MissingDataError, GatewayError, RequestError

from nose.tools import assert_equals, raises

@raises(DataValidationError)
def test_data_validation_error():
    """Testing DataValidationError"""
    try:
        raise DataValidationError("Your data is incorrect fool!")
    except DataValidationError as error:
        assert_equals("'Your data is incorrect fool!'", str(error))

    raise DataValidationError("Your data is incorrect fool!")

@raises(MissingDataError)
def test_missing_data_error():
    """Testing MissingDataError"""
    try:
        raise MissingDataError("Your data is incomplete fool!")
    except MissingDataError as error:
        assert_equals("'Your data is incomplete fool!'", str(error))

    raise MissingDataError("Your data is incomplete fool!")

@raises(GatewayError)
def test_gateway_error():
    """Testing GatewayError"""
    try:
        raise GatewayError("Your gateway sucks fool!")
    except GatewayError as error:
        assert_equals("'Your gateway sucks fool!'", str(error))

    raise GatewayError("Your gateway sucks fool!")

@raises(RequestError)
def test_request_error():
    """Testing RequestError"""
    try:
        raise RequestError("Your request is wrong fool!")
    except RequestError as error:
        assert_equals("'Your request is wrong fool!'", str(error))

    raise RequestError("Your request is wrong fool!")
