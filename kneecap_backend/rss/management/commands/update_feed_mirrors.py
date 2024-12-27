from django.core.management.base import BaseCommand
from rss.models import RSSFeed

class Command(BaseCommand):
    help = 'Updates mirrored content for all RSS feeds'

    def handle(self, *args, **options):
        feeds = RSSFeed.objects.all()
        updated_count = 0
        error_count = 0

        for feed in feeds:
            self.stdout.write(f"Updating feed: {feed.title}")
            success = feed.update_mirror()
            if success:
                updated_count += 1
            else:
                error_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Finished updating feeds. '
            f'Successfully updated: {updated_count}, '
            f'Errors: {error_count}, '
            f'Total feeds: {feeds.count()}'
        )) 