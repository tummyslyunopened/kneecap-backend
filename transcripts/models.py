from django.db import models
from subscriptions.models import Episode
from tools.models import TimeStampedModel
import logging


logger = logging.getLogger(__name__)


class TranscriptSegment(TimeStampedModel):
    episode = models.ForeignKey(
        Episode, related_name="transcript_segments", on_delete=models.CASCADE
    )

    start_time = models.CharField(max_length=100)
    end_time = models.CharField(max_length=100)
    text = models.CharField(max_length=1000)
