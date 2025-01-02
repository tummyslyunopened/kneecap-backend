from django.core.management.base import BaseCommand
from rss.models import Feed
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Downloads all images for each feed"

    def handle(self, *args, **options):
        feeds = Feed.objects.all()
        total_feeds = feeds.count()
        self.stdout.write(f"Found {total_feeds} feeds to download images for")
        success_count = 0
        fail_count = 0
        for feed in feeds:
            self.stdout.write(f"Downloading image for: {feed.title}")
            if feed.download_image():
                success_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully downloaded image for: {feed.title}")
                )
            else:
                fail_count += 1
                self.stdout.write(self.style.ERROR(f"Failed to download image for: {feed.title}"))
        self.stdout.write("\nDownload Summary:")
        self.stdout.write(f"Total feeds: {total_feeds}")
        self.stdout.write(self.style.SUCCESS(f"Successfully downloaded: {success_count}"))
        if fail_count:
            self.stdout.write(self.style.ERROR(f"Failed downloads: {fail_count}"))
