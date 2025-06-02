from django.db import models
from django.db.utils import IntegrityError
from subscriptions.models import Episode
from player.models import Player
from django.utils import timezone


# Create your models here.
class Minute(models.Model):
    """
    Represents a minute in the timeline. Each minute is unique in time.
    """

    created_at = models.DateTimeField(unique=True)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name="minutes")
    playback_time = models.IntegerField(default=0)

    @property
    def image(self):
        """Returns the image URL from the episode's subscription"""
        return self.episode.subscription.image_url

    @classmethod
    def record(cls):
        """
        Creates a new Minute instance for the given episode.
        Returns None if:
        - No active episode
        - A minute object already exists for the current minute
        """
        created_at = timezone.now().replace(second=0, microsecond=0)
        episode = Player.get_solo().episode
        if not episode:
            return None
        playback_time = episode.playback_time
        if not playback_time:
            playback_time = 0
        # Try to create a new minute object, return None if it already exists
        try:
            return cls.objects.create(
                created_at=created_at, episode=episode, playback_time=playback_time
            )
        except IntegrityError:
            return None

    def __str__(self):
        return f"{self.created_at.strftime('%Y-%m-%d')} - Minute {self.minute_of_day} ({self.created_at.strftime('%H:%M')})"
