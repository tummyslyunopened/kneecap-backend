from django.db import models
import logging
import uuid

logger = logging.getLogger(__name__)


class Subscription(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    link = models.URLField(unique=True)
    title = models.CharField(max_length=500, default="", blank=True, null=True)
    description = models.TextField(default="", blank=True, null=True)
    image_link = models.URLField(null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rss_url = models.URLField(null=True, blank=True)

    def refresh(self):
        pass

    @property
    def recent_episode(self):
        try:
            return self.episodes.latest("pub_date")
        except Episode.DoesNotExist:
            return None


class Episode(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    subscription = models.ForeignKey(
        Subscription, related_name="episodes", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    pub_date = models.DateTimeField()
    media_link = models.URLField(max_length=200, blank=True, null=True)
    audio_url = models.URLField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def image_url(self):
        return self.subscription.image_url

    def refresh(self):
        pass

    class Meta:
        unique_together = ("title", "description", "pub_date")


class SubscriptionRefreshQueue(models.Model):
    subscription = models.ForeignKey(
        Subscription, related_name="refreshes", on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def work(self):
        self.subscription.refresh()
        self.complete = True
        self.save()
