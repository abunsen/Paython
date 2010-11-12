"""core gateway class"""
# core exceptions
class CreditCardRequiredError(Exception):
    pass

class InvalidAmountError(Exception):
    pass

class Gateway(object):
    """base gateway class"""
    def __init__(self):
        """core gateway class"""
        pass

    def auth(self, amount=Decimal("0.01"), credit_card=None):
        """auth for a credit card"""
        if not credit_card:
            raise CreditCardRequiredError("a credit card is required to authorize")

        if amount < Decimal("0.00"):
            raise InvalidAmountError("we need more than {amount} to authorize this credit card".format(amount=amount))

        if not credit_card.is_valid():
            raise InvalidCreditCardError("{credit_card} is invalid".format(credit_card=credit_card))

        pass

    def settle(self):
        """settle a transaction"""
        pass

    def capture(self):
        """capture the sale"""
        pass

    def void(self):
        """void the sale"""
        pass

    def credit(self):
        """credit the sale"""
        pass
