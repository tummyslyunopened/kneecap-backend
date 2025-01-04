from django.shortcuts import render
from subscriptions.models import Subscription, Episode
# from datetime import datetime, timedelta


def dashboard(request):
    context = {
        "subscriptions": Subscription.objects.all(),
        "episodes": Episode.objects.all(),
        # "episodes": Episode.objects.filter(datetime.now() - timedelta(days=30)),
    }
    return render(request, "dashboard.html", context=context)
