from paython.exceptions import DataValidationError

class ECheck(object):
    """
    generic ECheck object
    """
    def __init__(self, aba_code, acct_num, acct_type, bank_name,first_name=None, last_name=None, acct_name=None, check_num=None, strict=False):
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

        self.strict = strict

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

    def __repr__(self):
        """
        string repr for debugging
        """
        return u'<eCheck -- {0.full_name}, aba_code: {0.aba_code}, acct_num: {0.account_num}, acct_type: {0.acct_type} \
                 bank_name: {0.bank_name}>, check_num: {0.check_num}'.format(self)


    def validate(self):
        """
        validates All Codes using util functions
        """
        if not is_valid_aba(self.aba_code):
            raise DataValidationError('The ABA Code doe not pass validation')
        return True
