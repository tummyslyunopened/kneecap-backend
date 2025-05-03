from django.core.management.base import BaseCommand
from subscriptions.models import Feed
import logging
import time

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Generate low quality versions of episodes continuously"

    def handle(self, *args, **options):
        while True:
            try:
                # Get episodes that need low quality versions
                episodes = (
                    Feed.get_solo()
                    .episodes.filter(audio_url__isnull=False, audio_url__gt="")
                    .exclude(low_quality_audio_url__isnull=False, low_quality_audio_url__gt="")
                    .order_by("duration")
                )

                if not episodes.exists():
                    logger.info("No episodes need low quality versions")
                    time.sleep(60)
                    continue

                logger.info(f"Processing {len(episodes)} episodes sequentially...")

                # Process each episode one at a time
                for episode in episodes:
                    try:
                        logger.info(
                            f"Starting low quality generation for episode: {episode.title} (duration: {episode.duration} seconds)"
                        )

                        success = episode.generate_low_quality_audio()
                        if success:
                            logger.info(f"Successfully processed episode: {episode.title}")
                        else:
                            logger.error(f"Failed to process episode: {episode.title}")
                    except Exception as e:
                        logger.error(f"Error processing episode {episode.title}: {str(e)}")

                time.sleep(60)

            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                time.sleep(60)
