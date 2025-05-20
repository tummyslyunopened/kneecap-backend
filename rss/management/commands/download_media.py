from django.core.management.base import BaseCommand
import logging
import time
from rss.models import RSSSubscription
from subscriptions.models import Episode
from tools.constants import HOUR_SECONDS


class Command(BaseCommand):
    help = "Downloads missing media for all RSS subscriptions."

    def handle(self, *args, **options):
        logger = logging.getLogger("rss.management.commands.download_media")
        self.stdout.write("Starting RSS Entry Media Downloader...")
        logger.info("Downloader started.")
        while True:
            episodes = Episode.objects.filter(audio_url="", hidden=False)
            logger.info(f"Found {episodes.count()} episodes missing audio.")
            for episode in episodes:
                msg = f"Downloading media for episode: {episode.title} (ID: {episode.pk})"
                self.stdout.write(msg)
                logger.info(msg)
                try:
                    result = RSSSubscription.objects.get(
                        pk=episode.subscription.pk
                    ).download_episode_audio(episode)
                    if result:
                        logger.info(
                            f"Successfully downloaded audio for episode: {episode.title} (ID: {episode.pk})"
                        )
                    else:
                        logger.warning(
                            f"No media URL or failed download for episode: {episode.title} (ID: {episode.pk})"
                        )
                except Exception as e:
                    logger.exception(
                        f"Exception while downloading media for episode {episode.pk}: {e}"
                    )
            time.sleep(HOUR_SECONDS / 2)
