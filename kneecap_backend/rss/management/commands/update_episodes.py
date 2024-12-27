from django.core.management.base import BaseCommand
from rss.models import Feed 

class Command(BaseCommand):
    help = 'Populate episodes for all RSS feeds'

    def handle(self, *args, **kwargs):
        feeds = Feed.objects.all()
        for feed in feeds:
            try:
                feed.populate_episodes()  # Call the existing method to populate episodes
                self.stdout.write(self.style.SUCCESS(f'Successfully populated episodes for {feed.title}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(F'{feed} - failed to populate {e}'))
                pass