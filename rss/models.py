from datetime import datetime, timedelta
from django.conf import settings
from django.db import models
from subscriptions.models import Queue, Subscription, Episode
from tools.media import download_media_requests
from tools.rss import parse_rss_entries, parse_rss_feed_info
import logging

logger = logging.getLogger(__name__)


class RSSSubscription(Subscription):
    def save(self, *args, **kwargs):
        self.refresh()
        super(RSSSubscription, self).save(*args, **kwargs)
        RSSSubscriptionRefreshQueue.objects.create(subscription=self)

    def refresh(self):
        self.title, self.description, self.image_link = parse_rss_feed_info(self.link)
        self.download_image()
        self.download_rss()

    def download_image(self):
        if not self.image_link:
            logger.warning(f"No external image link for feed: {self.title}")
            return (False, "")
        success, self.image_url = download_media_requests(
            self.image_link, str(self.uuid), "images", default_file_ext=".jpg"
        )
        self.image_url = self.image_url.replace(settings.SITE_URL.rstrip("/"), "")
        return (success, self.image_url)

    def download_rss(self):
        if not self.link:
            logger.warning(f"No external rss link for feed: {self.title}")
            return (False, "")
        success, self.rss_url = download_media_requests(
            self.link, str(self.uuid), media_path="rss", default_file_ext=""
        )
        self.rss_url = self.rss_url.replace(settings.SITE_URL.rstrip("/"), "")
        return (success, self.rss_url)

    def populate_recent_episodes(self):
        if not self.rss_url:
            logger.warn(f"no rss mirror found for subscription {self.title}")
            return False
        parse_success, entries = parse_rss_entries(
            "http://" + settings.SITE_URL.rstrip("/") + self.rss_url, "media_link", 7
        )
        for entry in entries:
            try:
                episode = Episode.objects.create(subscription=self, **entry)
                episode.save()
                RSSEpisodeDownloadQueue.objects.create(episode=episode)
            except Exception as e:
                logger.info(f"Failed to insert episode: {e}")
                pass 
        return parse_success 

    def download_episode_audio(episode: Episode):
        if not episode.media_link:
            logger.warning(f"No media URL for episode: {episode.title}")
            return False
        success, episode.audio_url = download_media_requests(
            episode.media_link, str(episode.uuid), media_path="episodes", default_file_ext=".mp3"
        )
        episode.audio_url = episode.audio_url.replace(settings.SITE_URL.rstrip("/"), "")
        episode.save()
        return success, episode.audio_url

    def populate_download_queue(self):
        for episode in self.recent_episodes:
            if not episode.audio_url:
                RSSEpisodeDownloadQueue.objects.create(episode=episode)

    @classmethod
    def refresh_all(cls):
        for subscription in cls.objects.all():
            RSSSubscriptionRefreshQueue.objects.get_or_create(
                subscription=subscription, completed=False
            )


class RSSSubscriptionRefreshQueue(Queue):
    subscription = models.ForeignKey(
        RSSSubscription, related_name="refreshes", null=True, blank=True, on_delete=models.SET_NULL
    )

    def save(self, *args, **kwargs):
        self.description = f"Refresh RSSSubscription {self.subscription.uuid}"
        super(RSSSubscriptionRefreshQueue, self).save(*args, **kwargs)

    def refresh(self):
        if self.subscription.last_refresh and datetime.now().replace(tzinfo=None) - self.subscription.last_refresh.replace(tzinfo=None) < timedelta(hours=1):
            print(f"Subscription not ready for refresh for {self.subscription.title}")
            return False 
        self.completed, x = self.subscription.download_rss()
        self.subscription.populate_recent_episodes()
        if self.completed:
            self.subscription.last_refresh = datetime.now().replace(tzinfo=None)
        self.save()
        return self.completed

class RSSEpisodeDownloadQueue(Queue):
    episode = models.ForeignKey(
        Episode, related_name="download_queue", null=True, blank=True, on_delete=models.SET_NULL
    )

    def save(self, *args, **kwargs):
        self.description = f"download episode: {self.episode}"
        super(RSSEpisodeDownloadQueue, self).save(*args, **kwargs)

    def download(self):
        self.completed, x = self.download_audio()
        self.save()
        return self.completed

    def download_audio(self):
        return RSSSubscription.download_episode_audio(self.episode)
