from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from subscriptions.models import Episode, Feed
from rss.forms import RSSSubscriptionForm
from rss.models import RSSSubscription, RSSEpisodeDownloadQueue
import logging
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)


def delete_rss_subscription(request, pk):
    rss_subscription = get_object_or_404(RSSSubscription, pk=pk)
    if request.method == "POST":
        rss_subscription.delete()
    return HttpResponse("<script>history.back();</script>")


def add_to_rss_episode_download_queue(request, pk):
    if request.method == "POST":
        episode = get_object_or_404(Episode, pk=pk)
        try:
            RSSEpisodeDownloadQueue.objects.create(episode=episode)
        except Exception as e:
            logger.warn(f"Request to view failed to add episode{e, request, episode}")
    return HttpResponse("<script>history.back();</script>")


def hide_episode(request, pk):
    episode = get_object_or_404(Episode, pk=pk)
    if request.method == "POST":
        episode.hidden = True
        episode.save()
    return HttpResponse("<script>history.back();</script>")


def toggle_feed_chronological(request):
    if request.method == "POST":
        feed = Feed.get_solo()
        feed.chronological = not feed.chronological
        feed.save()
    return HttpResponse("<script>history.back();</script>")


def hide_all_episodes(request):
    if request.method == "POST":
        feed = Feed.get_solo()
        for episode in feed.episodes:
            episode.hidden = True
            episode.save()
    return HttpResponse("<script>history.back();</script>")


def refresh_subscriptions(request):
    if request.method == "POST":
        RSSSubscription.refresh_all()
    return HttpResponse("<script>history.back();</script>")


def feed(request):
    if request.method == "POST":
        add_subscription_form = RSSSubscriptionForm(request.POST)
        if add_subscription_form.is_valid():
            rss_subscription = add_subscription_form.save(commit=False)
            rss_subscription.save()  # This will also run the `save` method in the `RSSSubscription` model
        return HttpResponseRedirect("/")
    else:
        add_subscription_form = RSSSubscriptionForm()
    context = {
        # "add_subscription_form": add_subscription_form,
        # "subscriptions": Subscription.objects.all(),
        "episodes": Feed.get_solo().episodes
        # "jobs": Queue.objects.all(),
        # "episodes": Episode.objects.filter(datetime.now() - timedelta(days=30)),
    }
    return render(request, "feed.html", context=context)
