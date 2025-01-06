from django.db import models

import logging

from tools.media import download_video_youtube_dl

logger = logging.getLogger(__name__)


class YoutubeSubscription:
    rss_url = models.URLField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super(YoutubeSubscription, self).save(*args, **kwargs)

    def download_audio(episode):
        download_video_youtube_dl(
            episode.media_url, episode.uuid, default_file_ext=".m4a", quality="best-audio"
        )
        pass
