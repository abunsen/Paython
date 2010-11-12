from lib.utils import get_card_type, get_card_exp, is_valid_exp, is_valid_cc, is_valid_cvv

class CreditCard(object):
    def __init__(self, name, number, exp_mo, exp_yr, cvv=None, cc_type=None, strict=False):
        """
        sets credit card info
        """
        self.name = name
        self.number = number
        self.exp_month = exp_mo
        self.exp_year = exp_yr
        self.strict = strict

        if strict:
            self.verification_value = cvv
            self.card_type = cc_type
        else:
            self.card_type = get_card_type(self.number)

    def __repr__(self):
        """
        for debugging
        """
        return u'%s, %s, %s, expires: %s' % (self.name, self.card_type, self.safe_num(), self.exp_date)

    @property
    def exp_date(self):
        """
        uses utils function
        """
        return get_card_exp(self.exp_month, self.exp_year)

    def safe_num(self):
        """
        outputs the card number with *'s, only exposing last four digits of card number
        """
        card_length = len(self.number)
        stars = '*'*(card_length-4)
        return '%s%s' % (stars, self.number[-4:])

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