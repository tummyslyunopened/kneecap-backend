from django import forms
from .models import RSSSubscription


class RSSSubscriptionForm(forms.ModelForm):
    class Meta:
        model = RSSSubscription
        fields = ["link"]  # Only the link field will be used to create a new RSSSubscription

    link = forms.URLField(
        label="RSS Feed Link",
        required=True,
        widget=forms.URLInput(attrs={"placeholder": "Enter RSS feed URL"}),
    )
