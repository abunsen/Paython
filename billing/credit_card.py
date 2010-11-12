"""credit card object""""
# core exceptions
class MissingCreditCardNumberError(Exception):
    pass

class MissingCreditCardExpError(Exception):
    pass

class MissingCreditCardNumberCvv(Exception):
    pass

# test credit cards
TEST_CREDIT_CARDS = [
    "378282246310005", # American Express
    "371449635398431", # American Express
    "378734493671000", # American Express Corporate
    "5610591081018250", # Australian BankCard
    "30569309025904", # Diners Club
    "38520000023237", # Diners Club
    "6011111111111117", # Discover
    "6011000990139424", # Discover
    "3530111333300000", # JCB
    "3566002020360505", # JCB
    "5555555555554444", # MasterCard
    "5105105105105100", # MasterCard
    "4111111111111111", # Visa
    "4012888888881881", # Visa
    "4222222222222", # Visa
    "76009244561", # Dankort (PBS)
    "5019717010103742", # Dankort (PBS)
    "6331101999990016", # Switch/Solo (Paymentech)
]

class CreditCard(object):
    """main credit card object implements validation"""
    number = None
    exp = None
    cvv = None

    def __init__(self, number=None exp=None, cvv=None):
        """init function, just change numbers, nothing special"""
        self.number = number
        self.exp = exp
        self.cvv = cvv

    def __unicode__(self):
        """gets the string representation"""
        return "{0.number}, {0.exp}, {0.cvv}".format(self)

    def __str__(self):
        """gets the string representation of the object"""
        return self.__unicode__()

    def _check_missing_attributes(self):
        """check if the object is complete, does not have any missing args"""
        if not number:
            raise MissingCreditCardNumberError("'{credit_card}' is missing a number".format(credit_card=self))
        elif not exp:
            raise MissingCreditCardExpError("'{credit_card}' is missing a exp date".format(credit_card=self))
        elif not cvv:
            raise MissingCreditCardNumberCvv("'{credit_card}' is missing a cvv".format(credit_card=self))

    def is_luhn_valid(self):
        """checks if the credit card is luhn valid, copied from: http://en.wikipedia.org/wiki/Luhn_algorithm"""
        num = [int(x) for x in self.number]
        return not sum(num[::-2] + [sum(divmod(d * 2, 10)) for d in num[-2::-2]]) % 10
