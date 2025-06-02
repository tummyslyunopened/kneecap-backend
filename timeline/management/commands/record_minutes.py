from django.core.management.base import BaseCommand
from timeline.models import Minute
import time
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Records a new minute every minute"

    def handle(self, *args, **options):
        self.stdout.write("Starting minute recorder...")
        logger.info("Minute recorder started.")

        try:
            while True:
                # Try to record a new minute
                new_minute = Minute.record()
                if new_minute:
                    msg = f"Recorded minute at {new_minute.created_at}"
                    self.stdout.write(self.style.SUCCESS(msg))
                    logger.info(msg)
                else:
                    logger.debug(
                        "No minute recorded - either no active episode or minute already exists"
                    )

                # Sleep until next minute
                time.sleep(60)
        except KeyboardInterrupt:
            self.stdout.write("\nMinute recorder stopped by user.")
            logger.info("Minute recorder stopped by user.")
