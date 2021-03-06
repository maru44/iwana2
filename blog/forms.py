from django import forms
from .models import *
from user.models import User

class WantedForm(forms.ModelForm):
    class Meta:
        model = Wanted
        fields = ['want_name', 'picture', 'want_price', 'want_intro']

class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['offer_url']