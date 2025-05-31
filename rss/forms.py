from django import forms
from .models import RSSSubscription


class RSSSubscriptionForm(forms.ModelForm):
    class Meta:
        model = RSSSubscription
        fields = ["link"]

    # link = forms.URLField(
    link = forms.CharField(
        label="RSS Feed Link",
        required=True,
        widget=forms.URLInput(attrs={"placeholder": "Enter RSS feed URL"}),
    )
