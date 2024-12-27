from django import forms
from .models import Subscription

class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['link']  # Only include the link field for the form