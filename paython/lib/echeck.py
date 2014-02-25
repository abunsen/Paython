from paython.exceptions import DataValidationError
from paython.lib.utils import is_valid_aba

class ECheck(object):
    """
    generic ECheck object
    """
    def __init__(self, aba_code, acct_num, acct_type, bank_name,first_name=None, last_name=None, acct_name=None, check_num=None,recurring_billing=None):
        """
        sets eCheck info
        """
        if acct_name:
            self.acct_name = acct_name
        else:
            self.first_name = first_name
            self.last_name = last_name
            self.acct_name = "{0.first_name} {0.last_name}".format(self)

        #everything else
        self.aba_code = aba_code
        self.acct_num = acct_num
        self.acct_type = acct_type
        self.bank_name = bank_name
        self.check_num = check_num
        self.recurring_billing = recurring_billing
    
    def __repr__(self):
        """
        string repr for debugging
        """
        return u'<eCheck -- {0.acct_name}, aba_code: {0.aba_code}, acct_num: {0.safe_num}, acct_type: {0.acct_type} \
                 bank_name: {0.bank_name}>, check_num: {0.check_num}'.format(self)


    @property
    def safe_num(self):
        """
        outputs the account number with *'s, only exposing last four digits of account number
        """
        account_length = len(self.acct_num)
        stars = '*' * (account_length - 4)
        return '{0}{1}'.format(stars, self.acct_num[-4:])

    def is_valid(self):
        """
        boolean to see if a Details is valid
        """
        try:
            self.validate()
        except DataValidationError:
            return False
        else:
            return True

    def validate(self):
        """
        validates All Codes using util functions
        """
        if not is_valid_aba(self.aba_code):
            raise DataValidationError('The ABA Code doe not pass validation')
        return True
