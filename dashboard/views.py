from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from subscriptions.models import Episode, Feed, Subscription
from rss.forms import RSSSubscriptionForm
from player.models import Player
import logging
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)


def delete_subscription(request, pk):
    subscription = get_object_or_404(Subscription, pk=pk)
    if request.method == "POST":
        subscription.delete()
    return HttpResponse("<script>history.back();</script>")


def hide_episode(request, pk):
    episode = get_object_or_404(Episode, pk=pk)
    if request.method == "POST":
        episode.hidden = True
        episode.save()
    return HttpResponse("<script>history.back();</script>")


def play_episode(request, pk):
    print("playing episode")
    episode = get_object_or_404(Episode, pk=pk)
    print(episode.title)
    if request.method == "POST":
        player = Player.get_solo()
        player.episode = episode
        player.save()
    return HttpResponse("<script>history.back();</script>")


def set_episode_playback_time(request):
    if request.method == "POST":
        playback_time = request.POST.get("currentTime")
        player = Player.get_solo()
        player.episode.playback_time = float(playback_time)
        player.episode.save()
        player.save()
    return HttpResponse("<script>history.back();</script>")


def toggle_feed_chronological(request):
    if request.method == "POST":
        feed = Feed.get_solo()
        feed.chronological = not feed.chronological
        feed.save()
    return HttpResponse("<script>history.back();</script>")


def update_feed_filter_preferences(request):
    if request.method == "POST":
        feed = Feed.get_solo()
        # Convert string 'true'/'false' to boolean
        has_audio = request.POST.get("has_audio", "false").lower()
        feed.has_audio = has_audio == "true"

        has_transcript = request.POST.get("has_transcript", "false").lower()
        feed.has_transcript = has_transcript == "true"

        feed.min_duration = int(request.POST.get("min_duration", 0))
        logger.warning(
            f"Updated feed preferences - has_audio: {feed.has_audio}, has_transcript: {feed.has_transcript}, min_duration: {feed.min_duration}"
        )
        feed.save()
    return HttpResponse("<script>history.back();</script>")


def toggle_feed_autoplay(request):
    if request.method == "POST":
        feed = Feed.get_solo()
        feed.autoplay_enabled = not feed.autoplay_enabled
        feed.save()
    return HttpResponse("<script>history.back();</script>")


def hide_all_episodes(request):
    if request.method == "POST":
        feed = Feed.get_solo()
        for episode in feed.episodes:
            episode.hidden = True
            episode.save()
    return HttpResponse("<script>history.back();</script>")


def subscriptions(request):
    if request.method == "POST":
        add_subscription_form = RSSSubscriptionForm(request.POST)
        if add_subscription_form.is_valid():
            rss_subscription = add_subscription_form.save(commit=False)
            rss_subscription.save()
            logger.info(f"Subscription added successfully: {rss_subscription}")
        else:
            logger.warning(f"Subscription form is invalid: {add_subscription_form.errors}")
        return HttpResponseRedirect("/subscriptions")
    else:
        add_subscription_form = RSSSubscriptionForm()
    context = {
        "add_subscription_form": add_subscription_form,
        "subscriptions": Subscription.objects.all(),
    }
    return render(request, "subscriptions.html", context=context)


def feed(request):
    if request.method == "POST":
        add_subscription_form = RSSSubscriptionForm(request.POST)
        if add_subscription_form.is_valid():
            rss_subscription = add_subscription_form.save(commit=False)
            rss_subscription.save()
            logger.info(f"Subscription added successfully: {rss_subscription}")
        else:
            logger.warning(f"Subscription form is invalid: {add_subscription_form.errors}")
        return HttpResponseRedirect("/")
    else:
        add_subscription_form = RSSSubscriptionForm()
    context = {
        "episodes": Feed.get_solo().episodes,
        "player_episode": Player.get_solo().episode,
        "feed": Feed.get_solo(),
        "add_subscription_form": add_subscription_form,
    }
    return render(request, "feed.html", context=context)
