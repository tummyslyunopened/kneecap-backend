from django.shortcuts import render, redirect
from .models import Subscription, Feed 
from .forms import SubscribeForm
from django.http import HttpResponse, Http404

def subscriptions(request):
    """Subscribe to External feeds"""
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            new_subscription = form.save()  # Save the new RSSFeed instance
            return redirect('subscriptions')  # Redirect to the same page after saving
    else:
        form = SubscribeForm()
    feeds = Subscription.objects.all()
    return render(request, 'subscriptions.html', {'form': form, 'feeds': feeds})

def mirror(request, uuid):
    """Serve the stripped feed."""
    try:
        stripped = Feed.objects.get(uuid=uuid)
        return HttpResponse(stripped.mirror, content_type='application/xml')
    except Feed.DoesNotExist:
        raise Http404("Hosted Stripped Feed not found.")
