from django.urls import path, include

# from rss import urls as rss_urls
# from api import urls as api_urls
from opml import urls as opml_urls
from django.conf import settings
from django.conf.urls.static import static
from dashboard.views import (
    feed,
    subscriptions,
    delete_rss_subscription,
    add_to_rss_episode_download_queue,
    hide_all_episodes,
    hide_episode,
    play_episode,
    toggle_feed_chronological,
    refresh_subscriptions,
    set_episode_playback_time
)

urlpatterns = [
    path("", feed, name="feed"),
    path("subscriptions", subscriptions, name="subscriptions"),
    path(
        "delete-rss-subscription/<int:pk>/",
        delete_rss_subscription,
        name="delete_rss_subscription",
    ),
    path(
        "add-to-rss-episode-download-queue/<int:pk>/",
        add_to_rss_episode_download_queue,
        name="add_to_rss_episode_download_queue",
    ),
    path(
        "hide-episode/<int:pk>/",
        hide_episode,
        name="hide_episode",
    ),
    path(
        "play-episode/<int:pk>/",
        play_episode,
        name="play_episode",
    ),
    path(
        "toggle-feed-chronological",
        toggle_feed_chronological,
        name="toggle_feed_chronological",
    ),
    path(
        "hide-all-episodes",
        hide_all_episodes,
        name="hide_all_episodes",
    ),
    path(
        "refresh-subscriptions",
        refresh_subscriptions,
        name="refresh_subscriptions",
    ),
    path(
        "set-episode-playback-time",
        set_episode_playback_time,
        name="set_episode_playback_time",
    ),
    # path("rss/", include(rss_urls)),
    # path("api/", include(api_urls)),
    path("api/opml/", include(opml_urls)),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
