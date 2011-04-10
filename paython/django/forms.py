from django import forms
from django.contrib.localflavor.us.forms import USStateField, USZipCodeField, USStateSelect

from paython.lib.utils import is_valid_cc, is_valid_cvv, is_valid_exp

class CustomerInformation(forms.Form):
    """
    Store the customer information, typically first name and last name.
    """
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)

class CreditCardForm(forms.Form):
    """
    Form for validating credit card numbers.
    """
    number = forms.CharField(max_length=19)
    exp_month = forms.CharField(max_length=2)
    exp_year = forms.CharField(max_length=4)
    security_code = forms.CharField(max_length=4)

    def clean(self):
        """Validates the form"""
        super(CreditCardForm, self).clean()

        cleaned_data = self.cleaned_data

        number = cleaned_data.get('number')
        security_code = cleaned_data.get('security_code')
        exp_month = cleaned_data.get('exp_month')
        exp_year = cleaned_data.get('exp_year')

        if not self.is_valid():
            raise forms.ValidationError("There was a problem processing your payment")

        if not is_valid_cc(number):
            raise forms.ValidationError("Invalid credit card number")

        if not is_valid_cvv(security_code):
            raise forms.ValidationError("Invalid security code")

        if not is_valid_exp(exp_month, exp_year):
            raise forms.ValidationError("Invalid expiracy date")

        return cleaned_data

class ZipCodeForm(forms.Form):
    """
    Sometimes we just need the zipcode
    """
    zipcode = USZipCodeField()

class CityStateZipCode(forms.Form):
    """
    And sometimes we need the City and State with the zipcode
    """
    city = forms.CharField(max_length=255)
    state = USStateField(widget=USStateSelect)
    zipcode = USZipCodeField()

class AddressForm(forms.Form):
    """
    Address form for new signup
    """
    address1 = forms.CharField(max_length=255)
    address2 = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=255)
    state = USStateField(widget=USStateSelect)
    zipcode = USZipCodeField()
