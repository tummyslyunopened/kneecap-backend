from django import forms
from .models import RSSFeed

class RSSFeedForm(forms.ModelForm):
    class Meta:
        model = RSSFeed
        fields = ['link']  # Only include the link field for the form