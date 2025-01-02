from django.shortcuts import render
from rss.models import Feed, Episode
from datetime import datetime, timedelta


def dashboard(request):
    context = {
        "feeds": Feed.objects.all(),
        "episodes": Episode.objects.filter(pub_date__gte=datetime.now() - timedelta(days=30)),
    }
    return render(request, "dashboard.html", context=context)
