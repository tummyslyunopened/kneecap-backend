from django.conf import settings
from subscriptions.models import Subscription, Episode
from tools.media import download_media_requests
from rss.parsers import parse_rss_feed_info, parse_rss_entries
import logging
from throttle.decorators import model_instance_throttle


logger = logging.getLogger(__name__)


class RSSSubscription(Subscription):
    def save(self, *args, **kwargs):
        if self.title == "":
            self.refresh()
        super(RSSSubscription, self).save(*args, **kwargs)

    def refresh(self):
        self.title, self.description, self.image_link = parse_rss_feed_info(self.link)
        self.download_image()
        self.download_rss()

    @model_instance_throttle("last_refresh", "refresh_interval", 1, 1)
    def throttled_refresh(self):
        print("throttle refresh")
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

    def rss_file_content(self):
        import os
        from django.conf import settings

        if not self.rss_url:
            logger.warning(f"no rss mirror found for subscription {self.title}")
            return None
        rss_url_rel = self.rss_url.lstrip("/\\")
        if rss_url_rel.lower().startswith("media/"):
            rss_url_rel = rss_url_rel[6:]
        media_root = str(settings.MEDIA_ROOT)
        rss_file_path = os.path.join(media_root, rss_url_rel)
        try:
            with open(rss_file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.warn(f"Failed to read RSS file for subscription {self.title}: {e}")
            return None

    def populate_recent_episodes(self):
        rss_content = self.rss_file_content()
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

    def download_episode_audio(episode: Episode):
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
