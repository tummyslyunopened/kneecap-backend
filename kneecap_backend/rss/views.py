from django.shortcuts import render, redirect
from .models import RSSFeed
from .forms import RSSFeedForm

def add_rss_feed(request):
    if request.method == 'POST':
        form = RSSFeedForm(request.POST)
        if form.is_valid():
            new_rss_feed = form.save()  # Save the new RSSFeed instance
            return redirect('add_rss_feed')  # Redirect to the same page after saving
    else:
        form = RSSFeedForm()

    # Retrieve all RSS feeds to display below the form
    rss_feeds = RSSFeed.objects.all()
    return render(request, 'add_rss_feed.html', {'form': form, 'rss_feeds': rss_feeds})