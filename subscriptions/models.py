from django.db import models
from datetime import timedelta, datetime
import uuid
import logging
from solo.models import SingletonModel

logger = logging.getLogger(__name__)


class Subscription(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    link = models.URLField(unique=True)
    title = models.CharField(max_length=500, default="", blank=True)
    description = models.TextField(default="", blank=True)
    image_link = models.URLField(blank=True)
    image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rss_url = models.URLField(blank=True)
    recent_episode_pub_date = models.DateTimeField(blank=True, null=True)
    last_refresh = models.DateTimeField(blank=True, null=True)

    @property
    def recent_episode(self):
        try:
            episode = self.episodes.latest("pub_date")
            self.recent_episode_pub_date = episode.pub_date
            return episode

        except Episode.DoesNotExist:
            return None

    @property
    def recent_episode_by_day_cuttoff(self):
        cut_off = datetime.now() - timedelta(days=7)
        return self.episodes.objects.filter(pub_date__gte=cut_off)

    class Meta:
        ordering = ["-recent_episode_pub_date"]


class Episode(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    subscription = models.ForeignKey(
        Subscription, related_name="episodes", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    pub_date = models.DateTimeField()
    media_link = models.URLField(max_length=200, blank=True)
    audio_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hidden = models.BooleanField(default=False)
    queued_for_download = models.BooleanField(default=False)
    duration = models.IntegerField(default=0)
    playback_time = models.IntegerField(default=0)

    class Meta:
        ordering = ["-pub_date"]
        unique_together = ("title", "description", "pub_date")

    @property
    def image_url(self):
        return self.subscription.image_url


class Feed(SingletonModel):
    chronological = models.BooleanField(default=False)
    view_hidden = models.BooleanField(default=False)
    cutoff_days = models.IntegerField(default=7)

    @property
    def order_string_pref(self):
        if self.chronological:
            return "-"
        else:
            return ""

    @property
    def episodes(self):
        return Episode.objects.filter(
            pub_date__gte=datetime.now() - timedelta(days=self.cutoff_days),
            hidden=(False or self.view_hidden),
        ).order_by(f"{self.order_string_pref}pub_date")


class Event(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class EpisodeWatchEvent(Event):
    episode = models.ForeignKey(Episode, related_name="watch_events", on_delete=models.CASCADE)
