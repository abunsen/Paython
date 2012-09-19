from paython.exceptions import DataValidationError

from paython.lib.utils import get_card_type, get_card_exp, is_valid_exp, is_valid_cc, is_valid_cvv

class CreditCard(object):
    """
    generic CreditCard object
    """
    def __init__(self, number, exp_mo, exp_yr, first_name=None, last_name=None, full_name=None, cvv=None, cc_type=None, strict=False):
        """
        sets credit card info
        """
        if full_name:
            self.full_name = full_name
        else:
            self.first_name = first_name
            self.last_name = last_name
            self.full_name = "{0.first_name} {0.last_name}".format(self)

        #everything else
        self.number = number
        self.exp_month = exp_mo
        self.exp_year = exp_yr
        self.exp_date = get_card_exp(self.exp_month, self.exp_year)
        self.card_type = get_card_type(self.number)

        self.verification_value = cvv if cvv else None

        self.strict = strict

    def __repr__(self):
        """
        string repr for debugging
        """
        if hasattr(self, '_exp_yr_style') and self._exp_yr_style:
            return u'<CreditCard -- {0.full_name}, {0.card_type}, {0.safe_num}, expires: {0.exp_date} --extra: {_exp_yr_style}>'.format(self, _exp_yr_style=self.exp_year[2:])
        else:
            return u'<CreditCard -- {0.full_name}, {0.card_type}, {0.safe_num}, expires: {0.exp_date}>'.format(self)

    @property
    def safe_num(self):
        """
        outputs the card number with *'s, only exposing last four digits of card number
        """
        card_length = len(self.number)
        stars = '*' * (card_length - 4)
        return '{0}{1}'.format(stars, self.number[-4:])

    def is_valid(self):
        """
        boolean to see if a card is valid
        """
        try:
            self.validate()
        except DataValidationError:
            return False
        else:
            return True

    def validate(self):
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

        return True
