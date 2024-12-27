from django.db import models
import feedparser
from dateutil import parser
import logging
import requests
from django.utils import timezone
import uuid
import os
from django.conf import settings

logger = logging.getLogger(__name__)


class Subscription(models.Model):
    link = models.URLField()
    title = models.CharField(max_length=500, default="")
    description = models.TextField(default="")
    pub_date = models.DateTimeField(auto_now_add=True)
    image = models.URLField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.title or not self.description:
            feed = feedparser.parse(self.link)
            self.title = feed.feed.title if not self.title else self.title
            self.description = (
                feed.feed.description if not self.description else self.description
            )
            self.image = (
                feed.feed.image.href
                if hasattr(feed.feed, "image") and hasattr(feed.feed.image, "href")
                else self.image
            )
        if self.pk is None:
            logger.info(f"Creating new RSSFeed: Title: {self.title}")
        super().save(*args, **kwargs)
        if self.pk and not hasattr(self, "mirror"):
            self.download()

    def download(self):
        try:
            response = requests.get(self.link)
            response.raise_for_status()
            mirror, created = Feed.objects.get_or_create(
                subscription=self,
                defaults={
                    "mirror": response.text,
                    "title": self.title,
                    "description": self.description,
                    "pub_date": self.pub_date,
                    "image": self.image,
                },
            )
            if not created:
                mirror.mirror = response.text
                mirror.save()
            self.last_updated = timezone.now()
            self.save()
            logger.info(f"Successfully updated mirror for feed: {self.title}")
            return True
        except Exception as e:
            logger.error(f"Failed to update mirror for feed {self.title}: {str(e)}")
            return False

    def __str__(self):
        return self.title


class Feed(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=500, default="")
    description = models.TextField(default="")
    pub_date = models.DateTimeField(auto_now_add=True)
    image = models.URLField(null=True, blank=True)
    subscription = models.OneToOneField(
        Subscription, on_delete=models.CASCADE, related_name="mirror", null=True
    )
    mirror = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def populate_episodes(self):
        try:
            if not (self.mirror and self.subscription):
                logger.warning(
                    f"No external feed found for feed: {self.title}. Skipping Episode Population."
                )
            if not (self.mirror):
                logger.warning(
                    f"No content found for feed: {self.title}. Attempting Download of external content."
                )
                self.subscription.download()
            feed = feedparser.parse(self.mirror)
            for entry in feed.entries:
                pub_date = parser.parse(entry.published)
                episode, created = Episode.objects.get_or_create(
                    feed=self,
                    title=entry.title,
                    pub_date=pub_date,
                    defaults={
                        "description": entry.description,
                        "media": entry.enclosures[0].url if entry.enclosures else None,
                    },
                )
                if created:
                    logger.info(
                        f"Created episode: Title: {episode.title}, Published: {episode.pub_date}, Podcast URL: {episode.media}"
                    )
                else:
                    logger.info(
                        f"Episode already exists: Title: {episode.title}, Published: {episode.pub_date}, Podcast URL: {episode.media}"
                    )
        except Exception as e:
            logger.error(f"Error populating episodes for feed {self.title}: {str(e)}")


class Episode(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    feed = models.ForeignKey(Feed, related_name="episodes", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    pub_date = models.DateTimeField()
    media = models.URLField(max_length=200, blank=True, null=True)
    played = models.BooleanField(default=False)
    current_playback_time = models.DurationField(blank=True, null=True)
    url = models.URLField(max_length=500, null=True, blank=True)

    def download(self):
        if not self.media:
            logger.warning(f"No media URL for episode: {self.title}")
            return False
        try:
            base_url = self.media.split("?")[0]
            file_extension = os.path.splitext(base_url)[-1] or ".mp3"
            filename = f"{self.uuid}{file_extension}"
            response = requests.get(self.media, stream=True)
            response.raise_for_status()
            os.makedirs(os.path.join(settings.MEDIA_ROOT, "episodes"), exist_ok=True)
            file_path = os.path.join("episodes", filename)
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            with open(full_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            url_path = (
                settings.MEDIA_URL.rstrip("/") + "/" + file_path.replace("\\", "/")
            )
            self.url = url_path
            self.save()
            logger.info(f"Successfully downloaded episode: {self.title}")
            return True
        except Exception as e:
            logger.error(f"Failed to download episode {self.title}: {str(e)}")
            return False

    def __str__(self):
        return self.title
