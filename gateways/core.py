from decimal import *

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
        for key, value in credit_card.__dict__.items():
            if not key.startswith('_'):
                try:
                    self.set(self.REQUEST_FIELDS[key]['f_name'], value)
                except:
                    pass # it is okay to fail (on exp_month & exp_year)

    def set_billing_info(self, address=None, city=None, state=None, zipcode=None, phone=None, email=None):
        """
        Set billing info, as necessary, no required keys. Validates email as well formed.
        """
        from Paython.lib.utils import is_valid_email

        if address:
            self.set(self.REQUEST_FIELDS['address']['f_name'], address)

        if city:
            self.set(self.REQUEST_FIELDS['city']['f_name'], city)

        if zipcode:
            self.set(self.REQUEST_FIELDS['zipcode']['f_name'], zipcode)

        if phone:
            self.set(self.REQUEST_FIELDS['phone']['f_name'], phone)

        if email:
            if is_valid_email(email):
                self.set(self.REQUEST_FIELDS['phone']['f_name'], email)
            else:
                raise DataValidationError('The email submitted does not pass regex validation')

    def set_shipping_info(self, ship_first_name, ship_last_name, ship_address, ship_city, ship_state, ship_zipcode, ship_country, ship_to_co=None, ship_phone=None, ship_email=None):
        """
        Adds shipping info, is standard on all gateways. Does not always use same all provided fields.
        """
        # setting all shipping variables
        self.set(self.REQUEST_FIELDS['ship_first_name']['f_name'], ship_first_name)
        self.set(self.REQUEST_FIELDS['ship_last_name']['f_name'], ship_last_name)
        self.set(self.REQUEST_FIELDS['ship_address']['f_name'], ship_address)
        self.set(self.REQUEST_FIELDS['ship_city']['f_name'], ship_city)
        self.set(self.REQUEST_FIELDS['ship_state']['f_name'], ship_state)
        self.set(self.REQUEST_FIELDS['ship_zipcode']['f_name'], ship_zipcode)
        self.set(self.REQUEST_FIELDS['ship_country']['f_name'], ship_country)

        # now optional ones
        optionals = ['ship_to_co', 'ship_phone', 'ship_email'] # using list of strings for reasons spec'd below

        #in line comments on this one
        for optional_var in optionals:
            exec '%s = %s' % (optional_var, optional_var) # re-assign each option param to itself
            if eval(optional_var): # see if it was passed into the method
                if optional_var not in self.REQUEST_FIELDS: # make sure we have a translation in the request fields dictionary
                    # & keep the string so we have a meaningful exception
                    raise MissingTranslationError('Gateway doesn\'t support the \"%s\" field for shipping' % optional_var)

                # set it on the gateway level if we are able to get this far
                self.set(self.REQUEST_FIELDS['ship_to_co']['f_name'], ship_to_co)

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
            if self.debug:
                print 'response: %s' % spec_response
                print 'field mapping: %s' % field_mapping

            for item in spec_response:
                iteration_key = str(i) #stringifying because the field_mapping keys are strings
                if iteration_key in field_mapping:
                    self.RESPONSE_FIELDS[field_mapping[iteration_key]] = item
                i += 1
        else: # dict settings
            for key, value in spec_response.items():
                self.RESPONSE_FIELDS[field_mapping[key]] = value

        #send it back!
        return self.RESPONSE_FIELDS