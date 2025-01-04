from django.db import models

# from tools.media import download_video_youtube_dl
import logging

logger = logging.getLogger(__name__)


class YoutubeSubscription:
    rss_url = models.URLField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super(YoutubeSubscription, self).save(*args, **kwargs)

    def download_audio(episode):
        pass
