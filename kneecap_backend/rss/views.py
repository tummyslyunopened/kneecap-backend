from django.shortcuts import render, redirect
from .models import Subscription, Feed
from .forms import SubscribeForm
from django.http import HttpResponse, Http404


def subscriptions(request):
    if request.method == "POST":
        form = SubscribeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("subscriptions")
    else:
        form = SubscribeForm()
    feeds = Subscription.objects.all()
    return render(request, "subscriptions.html", {"form": form, "feeds": feeds})


def mirror(request, uuid):
    try:
        feed = Feed.objects.get(uuid=uuid)
        return HttpResponse(feed.mirror, content_type="application/xml")
    except Feed.DoesNotExist:
        raise Http404("Hosted Stripped Feed not found.")
