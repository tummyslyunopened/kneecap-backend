from django.db import models
from datetime import timedelta, datetime
import uuid
import logging
from solo.models import SingletonModel
from tools.models import TimeStampedModel
from django.conf import settings
import os
from ffmpeg import FFmpeg

logger = logging.getLogger(__name__)


class Subscription(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    link = models.URLField(unique=True)
    title = models.CharField(max_length=500, default="", blank=True)
    description = models.TextField(default="", blank=True)
    image_link = models.URLField(blank=True)
    image_url = models.URLField(blank=True)
    rss_url = models.URLField(blank=True)
    recent_episode_pub_date = models.DateTimeField(blank=True, null=True)
    last_refresh = models.DateTimeField(blank=True, null=True)
    refresh_interval = models.IntegerField(blank=True, null=True)
    last_media_download = models.DateTimeField(blank=True, null=True)
    media_download_interval = models.IntegerField(blank=True, null=True)

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
        return self.episodes.filter(pub_date__gte=cut_off)

    class Meta:
        ordering = ["-recent_episode_pub_date"]

    @property
    def rss_file_path(self):
        if not self.rss_url:
            logger.warning(f"no rss mirror found for subscription {self.title}")
            return None
        rss_url_rel = self.rss_url.lstrip("/\\")
        if rss_url_rel.lower().startswith("media/"):
            rss_url_rel = rss_url_rel[6:]
        media_root = str(settings.MEDIA_ROOT)
        return os.path.join(media_root, rss_url_rel)

    @property
    def rss_file_content(self):
        try:
            with open(self.rss_file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.warn(f"Failed to read RSS file for subscription {self.title}: {e}")
            return None


class Episode(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    subscription = models.ForeignKey(
        Subscription, related_name="episodes", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    pub_date = models.DateTimeField()
    scheduled_date = models.DateTimeField(null=True, blank=True)
    media_link = models.URLField(max_length=200, blank=True)
    audio_url = models.URLField(max_length=500, blank=True)
    low_quality_audio_url = models.URLField(max_length=500, blank=True)
    transcript_url = models.URLField(max_length=500, blank=True)
    hidden = models.BooleanField(default=False)
    duration = models.IntegerField(default=0)
    playback_time = models.IntegerField(default=0)

    class Meta:
        ordering = ["-pub_date"]
        unique_together = ("title", "description", "pub_date")

    def generate_low_quality_audio(self):
        """
        Generate a low-quality version of the audio using ffmpeg.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the original audio file path
            original_path = self.derive_audio_file_path
            if not original_path:
                logger.warning(f"No audio file path for episode {self.title}")
                return False

            # Get the output path
            output_path = self.derive_low_quality_file_path
            if not output_path:
                logger.warning(f"Could not derive low quality file path for episode {self.title}")
                return False

            # Ensure the directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Run ffmpeg to create low quality version using python-ffmpeg
            ffmpeg = (
                FFmpeg()
                .option("y")  # overwrite output file if it exists
                .input(original_path)
                .output(
                    output_path,
                    {
                        "ac": 1,  # Mono audio
                        "ar": "11025",  # 22.05kHz sample rate (increased for better quality)
                        "ab": "16k",  # 32kbps audio quality (increased for better quality)
                        # "af": "highpass=f=200, lowpass=f=3000, volume=1.5",  # Audio filters: remove low and high frequency noise, boost volume slightly
                    },
                )
            )
            ffmpeg.execute()

            # Update the low quality audio URL
            self.low_quality_audio_url = self.derive_low_quality_url
            self.save()
            logger.info(f"Successfully created low quality audio for episode {self.title}")
            return True

        except Exception as e:
            logger.error(f"Failed to create low quality audio for episode {self.title}: {e}")
            return False

    @property
    def duration_str(self):
        """Return duration as HH:mm:ss string"""
        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @property
    def derive_audio_file_path(self):
        if not self.audio_url:
            logger.warning(f"no audio mirror found for episode {self.title}")
            return None
        audio_url_rel = self.audio_url.replace(settings.MEDIA_URL, "").lstrip("/\\")
        if audio_url_rel.lower().startswith("media/"):
            audio_url_rel = audio_url_rel[6:]
        media_root = str(settings.MEDIA_ROOT)
        return os.path.normpath(os.path.join(media_root, audio_url_rel))

    @property
    def image_url(self):
        return self.subscription.image_url

    @property
    def derive_low_quality_file_path(self):
        """
        Get the path for the low quality audio file.

        Returns:
            str: Path to the low quality audio file
        """
        if not self.audio_url:
            logger.warning(f"no audio mirror found for episode {self.title}")
            return None

        # Get the relative path from media root
        rel_path = self.audio_url.replace(settings.MEDIA_URL, "").lstrip("/\\")
        if rel_path.lower().startswith("media/"):
            rel_path = rel_path[6:]

        # Replace episodes with episodes-low
        low_rel_path = rel_path.replace("episodes/", "episodes-low/")

        # Create the full path
        media_root = str(settings.MEDIA_ROOT)
        return os.path.normpath(os.path.join(media_root, low_rel_path))

    @property
    def derive_low_quality_url(self):
        """
        Get the URL for the low quality audio file by converting the file path to a URL.

        Returns:
            str: URL to the low quality audio file
        """
        file_path = self.derive_low_quality_file_path
        if not file_path:
            logger.warning(f"no low quality file path found for episode {self.title}")
            return None

        # Convert file path to URL by replacing MEDIA_ROOT with MEDIA_URL
        rel_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
        return settings.MEDIA_URL + rel_path.replace(os.sep, "/")

    @property
    def derive_transcript_file_path(self):
        if not self.derive_audio_file_path:
            logger.warning(f"no audio mirror found for episode {self.title}")
            return None
        rel_path = os.path.relpath(self.derive_audio_file_path, settings.MEDIA_ROOT)
        transcript_rel = rel_path.replace("episodes", "transcripts") + ".json"
        return os.path.normpath(os.path.join(settings.MEDIA_ROOT, transcript_rel))

    @property
    def derive_transcript_url(self):
        if not self.derive_transcript_file_path:
            logger.warning(f"no transcript file found for episode {self.title}")
            return None
        rel_path = os.path.relpath(self.derive_transcript_file_path, settings.MEDIA_ROOT)
        return settings.MEDIA_URL + rel_path.replace(os.sep, "/")


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
