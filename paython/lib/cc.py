"""
cc.py - CreditCard object to pass to gateway to proccess
"""

from Paython.exceptions import DataValidationError
from utils import get_card_type, get_card_exp, is_valid_exp, is_valid_cc, is_valid_cvv

class CreditCard(object):
    def __init__(self, number, exp_mo, exp_yr, first_name=None, last_name=None, full_name=None, cvv=None, cc_type=None, strict=False):
        """
        sets credit card info

        strict: cvv and cc_type required
        not strict: cc_type is guessed cvv is not required
        """
        if full_name:
            self.full_name = full_name
        else:
            self.first_name = first_name
            self.last_name = last_name
            self.full_name = '%s %s' % (self.first_name, self.last_name)

        #everything else
        self.number = number
        self.exp_month = exp_mo
        self.exp_year = exp_yr
        self.exp_date = get_card_exp(self.exp_month, self.exp_year)
        self.card_type = get_card_type(self.number)

        if cvv:
            self.verification_value = cvv

    def __unicode__(self):
        """
        unicode representation of the object
        """
        return u'{0.name}, {0.card_type}, {0.safe_num}, {0.exp_date}'.format(self)

    def __str__(self):
        """
        string representation of the credit card
        """
        return self.__unicode__()

    def __repr__(self):
        """
        credit card object representation
        """
        return u'<CreditCard -- {0.name}, {0.card_type}, {0.safe_num}, expires: {0.exp_date} --extra: {0._exp_yr_style}>'.format(self)

    def _validate(self):
        """
        validates expiration date & card number using util functions
        """
        if not is_valid_cc(self.number):
            raise DataValidationError('The credit card number provided does not pass luhn validation')

        if not is_valid_exp(self.exp_month, self.exp_year):
            raise DataValidationError('The credit card expiration provided is not in the future')

        if self.strict:
            if not is_valid_cvv(self.verification_value):
                raise DataValidationError('The credit card cvv is not valid')

    def is_valid(self):
        """
        boolean to see if a card is valid
        """
        try:
            self._validate()
        except DataValidationError:
            return False

        return True

    @property
    def safe_num(self):
        """
        outputs the card number with *'s, only exposing last four digits of card number
        """
        stars = '*' * (len(self.number) - 4)
        return '{stars}{last_4}'.format(stars=stars, last_4=self.number[-4:])
