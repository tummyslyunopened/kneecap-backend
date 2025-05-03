from django.conf import settings
from django.utils import timezone
from subscriptions.models import Subscription, Episode
from throttle.decorators import model_instance_throttle
from tools.constants import HOUR_SECONDS
from tools.media import download_media_requests
from rss.parsers import (
    parse_rss_feed_info,
    parse_rss_entries,
    parse_rss_feed_info_reader,
    parse_rss_entries_reader,
)
import logging


logger = logging.getLogger(__name__)


class RSSSubscription(Subscription):
    def save(self, *args, **kwargs):
        if self.id is None:
            self.rss_url = self.download_rss()[1]
            self.title, self.description, self.image_link = parse_rss_feed_info(self.link)
            self.image_url = self.download_image()[1]
            self.populate_recent_episodes()
            logger.info("\n".join(f"{k} = {v}" for k, v in self.__dict__.items()))
        super(RSSSubscription, self).save(*args, **kwargs)

    def refresh(self):
        print(self.image_link)
        if getattr(settings, "USE_READER_BACKEND", True) and self.image_link != "":
            self.title, self.description = parse_rss_feed_info_reader(self.link)
        else:
            self.title, self.description, self.image_link = parse_rss_feed_info(self.link)
        _, self.rss_url = self.download_rss()
        self.populate_recent_episodes()
        self.last_refresh = timezone.now()
        self.save()

    @model_instance_throttle(
        "last_refresh", "refresh_interval", 4 * HOUR_SECONDS, 4 * HOUR_SECONDS
    )
    def throttled_refresh(self):
        self.refresh()

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
        if getattr(settings, "USE_READER_BACKEND", False):
            parse_success, entries = parse_rss_entries_reader(self.rss_url, 7)
        else:
            rss_content = self.rss_file_content
            if not rss_content:
                return False
            parse_success, entries = parse_rss_entries(rss_content, 7)
        for entry in entries:
            try:
                episode = Episode.objects.create(subscription=self, **entry)
                episode.save()
            except Exception as e:
                logger.info(f"Failed to insert episode: {e}")
                pass
        return parse_success

    @model_instance_throttle(
        "last_media_download", "media_download_interval", HOUR_SECONDS, HOUR_SECONDS
    )
    def download_episode_audio(self, episode: Episode):
        if not episode.media_link:
            logger.warning(f"No media URL for episode: {episode.title}")
            return False
        if episode.audio_url:
            logger.warning(f"Audio already downloaded for episode: {episode.title}")
            return True
        success, episode.audio_url = download_media_requests(
            episode.media_link, str(episode.uuid), media_path="episodes", default_file_ext=".mp3"
        )
        episode.audio_url = episode.audio_url.replace(settings.SITE_URL.rstrip("/"), "")
        episode.save()
        return success, episode.audio_url

    def refresh_reader(self):
        """
        Alternative refresh using lemon24/reader for fetching/parsing feed info.
        """
        self.title, self.description, self.image_link = parse_rss_feed_info_reader(self.link)
        self.download_image()
        self.download_rss()

    def populate_recent_episodes_reader(self):
        """
        Alternative episode population using lemon24/reader for fetching/parsing entries.
        """
        parse_success, entries = parse_rss_entries_reader(self.link, 7)
        for entry in entries:
            try:
                episode = Episode.objects.create(subscription=self, **entry)
                episode.save()
            except Exception as e:
                logger.info(f"Failed to insert episode: {e}")
                pass
        return parse_success
