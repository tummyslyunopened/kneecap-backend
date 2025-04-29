from django.core.management.base import BaseCommand
from rss.models import RSSSubscription
import time
import logging
from tools.constants import HOUR_SECONDS

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Continuously refreshes all RSS subscriptions and downloads missing episode audio."

    def add_arguments(self, parser):
        parser.add_argument(
            "--interval",
            type=int,
            default=HOUR_SECONDS,
            help="Seconds to wait between sync cycles (default: 3600)",
        )

    def handle(self, *args, **options):
        interval = options["interval"]
        self.stdout.write(
            f"Starting continuous RSS sync (interval: {interval}s). Press Ctrl+C to stop."
        )
        try:
            while True:
                subscriptions = RSSSubscription.objects.order_by("last_refresh")
                total = subscriptions.count()
                self.stdout.write(
                    f"Sync cycle: Processing {total} subscriptions (least recently refreshed first)..."
                )
                for i, subscription in enumerate(subscriptions, 1):
                    try:
                        self.stdout.write(
                            f"[{i}/{total}] Refreshing {subscription.title or subscription.link} (last_refresh: {subscription.last_refresh})..."
                        )
                        subscription.throttled_refresh()
                    except Exception as e:
                        logger.exception(f"Error processing subscription {subscription.pk}: {e}")
                        self.stderr.write(f"Error processing subscription {subscription.pk}: {e}")
                self.stdout.write(f"Sync cycle complete. Sleeping for {interval} seconds...\n")
                time.sleep(interval)
        except KeyboardInterrupt:
            self.stdout.write("Continuous RSS sync stopped by user.")
