import time
from paython.exceptions import GatewayError
from paython.gateways.authorize_net import AuthorizeNet
import requests
import copy

class AuthECheckDotNet(AuthorizeNet):
    REQUEST_FIELDS=copy.deepcopy(AuthorizeNet.REQUEST_FIELDS)
    REQUEST_FIELDS.update({
                             'aba_code':'x_bank_aba_code',
                             'acct_num':'x_bank_acct_num',
                             'acct_type':'x_bank_acct_type',
                             'bank_name':'x_bank_name',
                             'acct_name':'x_bank_acct_name',
                             'echeck_type':'x_echeck_type',
                             'check_num':'x_bank_check_number',
                             'recurring_billing':'x_recurring_billing',
                           })


    def __init__(self, username='test', password='testpassword', debug=False, test=False, delim=None):
        #Set Required Values
        super(AuthECheckDotNet, self).__init__(username=username, password=password,
                           debug=debug, test=test,delim=delim)
        # Update Fields to bubble up to Base Class
        super(AuthorizeNet, self).__init__(translations=self.REQUEST_FIELDS, debug=debug)
      

    def auth(self, amount, echeck_type=None, bank_account=None, billing_info=None, shipping_info=None, invoice_num=None, duplicate_window=120, customer_ip=None):
        """
        Sends Bank and Check details for authorization
        """
        #set up transaction
        super(AuthECheckDotNet,self).charge_setup()
        """ Change Method to Echeck Instead of CC """
        super(AuthECheckDotNet, self).set('x_method', 'ECHECK')
        #setting transaction data
        super(AuthECheckDotNet, self).set(self.REQUEST_FIELDS['amount'], amount)
        super(AuthECheckDotNet, self).set(self.REQUEST_FIELDS['trans_type'], 'AUTH_ONLY')
        super(AuthECheckDotNet, self).set(self.REQUEST_FIELDS['duplicate_window'], duplicate_window)
        if customer_ip:
            super(AuthorizeNet, self).set(self.REQUEST_FIELDS['ip'], customer_ip)

        if not echeck_type:
            debug_string = "No Echeck Type Given"
            logger.debug(debug_string)
            raise MissingDataError('You did not pass an ECheck Type')
        else:
            super(AuthECheckDotNet, self).set(self.REQUEST_FIELDS['echeck_type'], echeck_type)

        if invoice_num is not None:
            super(AuthECheckDotNet, self).set(self.REQUEST_FIELDS['invoice_num'], invoice_num)

        # validating or building up request
        if not bank_account:
            debug_string = "No Account object present. You passed in %s " % (bank_account)
            logger.debug(debug_string)
            raise MissingDataError('You did not pass an account object into the arc method')
        else:
            super(AuthECheckDotNet, self).use_echeck(bank_account)

        #Set Conditionally Required Fields
        if echeck_type == 'ARC' or echeck_type == 'BOC':
            super(AuthECheckDotNet, self).set(self.REQUEST_FIELDS['check_num'], bank_account.check_num)
        elif echeck_type == 'WEB' or echeck_type == 'TEL':
            super(AuthECheckDotNet, self).set(self.REQUEST_FIELDS['recurring_billing'], bank_account.recurring_billing)
            
        if billing_info:
            super(AuthECheckDotNet, self).set_billing_info(**billing_info)

        if shipping_info:
            super(AuthECheckDotNet, self).set_shipping_info(**shipping_info)

        # send transaction to gateway!
        response, response_time = super(AuthECheckDotNet,self).request()
        return super(AuthECheckDotNet,self).parse(response, response_time)
        
    def capture(self, amount, echeck_type=None, bank_account=None, billing_info=None, shipping_info=None, invoice_num=None, duplicate_window=120):
        """
        Sends Bank and Check details for authorization
        """
        #set up transaction
        super(AuthECheckDotNet,self).charge_setup()
        """ Change Method to Echeck Instead of CC """
        super(AuthECheckDotNet, self).set('x_method', 'ECHECK')
        #setting transaction data
        super(AuthECheckDotNet, self).set(self.REQUEST_FIELDS['amount'], amount)
        super(AuthECheckDotNet, self).set(self.REQUEST_FIELDS['trans_type'], 'AUTH_CAPTURE')
        super(AuthECheckDotNet, self).set(self.REQUEST_FIELDS['duplicate_window'], duplicate_window)

        if not echeck_type:
            debug_string = "No Echeck Type Given"
            logger.debug(debug_string)
            raise MissingDataError('You did not pass an ECheck Type')
        else:
            super(AuthECheckDotNet, self).set(self.REQUEST_FIELDS['echeck_type'], echeck_type)

        if invoice_num is not None:
            super(AuthECheckDotNet, self).set(self.REQUEST_FIELDS['invoice_num'], invoice_num)

        # validating or building up request
        if not bank_account:
            debug_string = "No Account object present. You passed in %s " % (bank_account)
            logger.debug(debug_string)
            raise MissingDataError('You did not pass an account object into the arc method')
        else:
            super(AuthECheckDotNet, self).use_echeck(bank_account)

        #Set Conditionally Required Fields
        if echeck_type == 'ARC' or echeck_type == 'BOC':
            super(AuthECheckDotNet, self).set(self.REQUEST_FIELDS['check_num'], bank_account.check_num)
        elif echeck_type == 'WEB' or echeck_type == 'TEL':
            super(AuthECheckDotNet, self).set(self.REQUEST_FIELDS['recurring_billing'], bank_account.recurring_billing)
            
        if billing_info:
            super(AuthECheckDotNet, self).set_billing_info(**billing_info)

        if shipping_info:
            super(AuthECheckDotNet, self).set_shipping_info(**shipping_info)

        # send transaction to gateway!
        response, response_time = super(AuthECheckDotNet,self).request()
        return super(AuthECheckDotNet,self).parse(response, response_time)


