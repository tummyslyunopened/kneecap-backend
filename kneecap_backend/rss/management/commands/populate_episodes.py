from django.core.management.base import BaseCommand
from rss.models import RSSFeed

class Command(BaseCommand):
    help = 'Populate episodes for all RSS feeds'

    def handle(self, *args, **kwargs):
        feeds = RSSFeed.objects.all()
        for feed in feeds:
            feed.populate_episodes()  # Call the existing method to populate episodes
            self.stdout.write(self.style.SUCCESS(f'Successfully populated episodes for {feed.title}'))