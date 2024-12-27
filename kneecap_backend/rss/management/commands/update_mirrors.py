from django.core.management.base import BaseCommand
from rss.models import Subscription


class Command(BaseCommand):
    help = "Updates mirrored content for all RSS feeds"

    def handle(self, *args, **options):
        subscriptions = Subscription.objects.all()
        updated_count = 0
        error_count = 0
        for subscription in subscriptions:
            self.stdout.write(f"Updating feed: {subscription.title}")
            success = subscription.download()
            if success:
                self.stdout.write(f"Successfully updated feed: {subscription.title}")
                updated_count += 1
            else:
                self.stdout.write(f"Failed to update feed: {subscription.title}")
                error_count += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Finished updating feeds. "
                f"Successfully updated: {updated_count}, "
                f"Errors: {error_count}, "
                f"Total feeds: {subscriptions.count()}"
            )
        )
