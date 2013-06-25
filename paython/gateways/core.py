"""core.py - Paython's core libraries"""

import logging

from paython.exceptions import DataValidationError, MissingTranslationError
from paython.lib.utils import is_valid_email

logger = logging.getLogger(__name__)

class Gateway(object):
    """base gateway class"""
    REQUEST_FIELDS = {}
    RESPONSE_FIELDS = {}
    debug = False

    def __init__(self, set_method, translations, debug):
        """core gateway class"""
        self.set = set_method
        self.REQUEST_FIELDS = translations
        self.debug = debug

    def use_credit_card(self, credit_card):
        """
        Set up credit card info use (if necessary for transaction)
        """
        if hasattr(credit_card, '_exp_yr_style'): # here for gateways that like 2 digit expiration years
            credit_card.exp_year = credit_card.exp_year[-2:]

        for key, value in credit_card.__dict__.items():
            if not key.startswith('_'):
                try:
                    self.set(self.REQUEST_FIELDS[key], value)
                except KeyError:
                    pass # it is okay to fail (on exp_month & exp_year)

    def set_billing_info(self, address=None, address2=None, city=None, state=None, zipcode=None, country=None, phone=None, email=None, ip=None, first_name=None, last_name=None):
        """
        Set billing info, as necessary, no required keys. Validates email as well formed.
        """
        if address:
            self.set(self.REQUEST_FIELDS['address'], address)

        if address2:
            self.set(self.REQUEST_FIELDS['address2'], address2)

        if city:
            self.set(self.REQUEST_FIELDS['city'], city)

        if state:
            self.set(self.REQUEST_FIELDS['state'], state)

        if zipcode:
            self.set(self.REQUEST_FIELDS['zipcode'], zipcode)

        if country:
            self.set(self.REQUEST_FIELDS['country'], country)

        if phone:
            self.set(self.REQUEST_FIELDS['phone'], phone)

        if ip:
            self.set(self.REQUEST_FIELDS['ip'], ip)

        if first_name:
            self.set(self.REQUEST_FIELDS['first_name'], first_name)

        if last_name:
            self.set(self.REQUEST_FIELDS['last_name'], last_name)

        if email:
            if is_valid_email(email):
                self.set(self.REQUEST_FIELDS['email'], email)
            else:
                raise DataValidationError('The email submitted does not pass regex validation')

    def set_shipping_info(self, ship_first_name, ship_last_name, ship_address, ship_city, ship_state, ship_zipcode, ship_country=None, ship_to_co=None, ship_phone=None, ship_email=None):
        """
        Adds shipping info, is standard on all gateways. Does not always use same all provided fields.
        """
        # setting all shipping variables
        self.set(self.REQUEST_FIELDS['ship_first_name'], ship_first_name)
        self.set(self.REQUEST_FIELDS['ship_last_name'], ship_last_name)
        self.set(self.REQUEST_FIELDS['ship_address'], ship_address)
        self.set(self.REQUEST_FIELDS['ship_city'], ship_city)
        self.set(self.REQUEST_FIELDS['ship_state'], ship_state)
        self.set(self.REQUEST_FIELDS['ship_zipcode'], ship_zipcode)

        # now optional ones
        optionals = ['ship_to_co', 'ship_phone', 'ship_email', 'ship_country'] # using list of strings for reasons spec'd below

        #in line comments on this one
        for optional_var in optionals:
            exec '%s = %s' % (optional_var, optional_var) # re-assign each option param to itself
            if eval(optional_var): # see if it was passed into the method
                if optional_var not in self.REQUEST_FIELDS: # make sure we have a translation in the request fields dictionary
                    # & keep the string so we have a meaningful exception
                    raise MissingTranslationError('Gateway doesn\'t support the \"%s\" field for shipping' % optional_var)

                # set it on the gateway level if we are able to get this far
                self.set(self.REQUEST_FIELDS['ship_to_co'], ship_to_co)

    def standardize(self, spec_response, field_mapping, response_time, approved):
        """
        Translates gateway specific response into Paython generic response.
        Expects list or dictionary for spec_repsonse & dictionary for field_mapping.
        """
        # manual settings
        self.RESPONSE_FIELDS['response_time'] = response_time
        self.RESPONSE_FIELDS['approved'] = approved

        if isinstance(spec_response, list): # list settings
            i = 0
            debug_string = 'paython.gateways.core.standardize() -- spec_response: '
            logger.debug(debug_string.center(80, '='))
            logger.debug('\n%s' % spec_response)
            debug_string = 'paython.gateways.core.standardize() -- field_mapping: '
            logger.debug(debug_string.center(80, '='))
            logger.debug('\n%s' % field_mapping)

            for item in spec_response:
                iteration_key = str(i) #stringifying because the field_mapping keys are strings
                if iteration_key in field_mapping:
                    self.RESPONSE_FIELDS[field_mapping[iteration_key]] = item
                i += 1
        else: # dict settings
            for key, value in spec_response.items():
                try:
                    self.RESPONSE_FIELDS[field_mapping[key]] = value
                except KeyError:
                    pass #its okay to fail if we dont have a translation

        #send it back!
        return self.RESPONSE_FIELDS
