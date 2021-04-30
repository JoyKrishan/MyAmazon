from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import BillingAddress
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import EMPTY_VALUES

PAYMENT_OPTIONS = [
    ('S', 'Stripe'),
    ('P', 'Paypal')
]


class CheckoutForm(forms.ModelForm):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        "placeholder": "1234 Main St", 'id': "address", 'class': "form-control"
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'id': "address-2", 'class': "form-control", 'placeholder': "Apartment or suite"
    }))
    zip_code = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': '2312', "class": "form-control"
    }))
    country = CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(attrs={
        "class": "custom-select d-block w-100"}
    ))
    shipping_address = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={
        'class': 'custom - control - input'
    }))
    save_info = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={
        'class': 'custom - control - input'
    }))
    payment_method = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_OPTIONS)

    class Meta:
        model = BillingAddress
        fields = [
            "street_address",
            "apartment_address",
            "zip_code",
            "country",
            "shipping_address",
            "save_info",
        ]


class CouponForm(forms.Form):
    code = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': "form-control", 'placeholder': "Promo code",
        'aria - label': "Recipient's username",
        'aria - describedby': "basic-addon2"
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField(max_length=20)
    email = forms.EmailField()
    reason = forms.CharField(widget=forms.Textarea(attrs={
        "row": 4
    }))


