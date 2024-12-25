from django.core.management.base import BaseCommand
from rss.models import RSSFeed
from mirror.models import RSSMirror
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create and update mirrors for all RSS feeds'

    def handle(self, *args, **kwargs):
        feeds = RSSFeed.objects.all()
        self.stdout.write(f'Processing {feeds.count()} feeds...')

        for feed in feeds:
            try:
                # Get or create mirror for this feed
                mirror, created = RSSMirror.objects.get_or_create(
                    external_feed=feed,
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Created new mirror for {feed.title}')
                    )
                
                # Update the mirror content
                success = mirror.update_mirror()
                if success:
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully updated mirror for {feed.title}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Failed to update mirror for {feed.title}')
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing {feed.title}: {str(e)}')
                )
                logger.error(f'Error processing feed {feed.id}: {str(e)}', exc_info=True) 