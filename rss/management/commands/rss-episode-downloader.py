from django.core.management.base import BaseCommand
from rss.models import RSSEpisodeDownloadQueue


class Command(BaseCommand):
    help = "Download RSS Episode Audio Content"

    def handle(self, *args, **options):
        queue = RSSEpisodeDownloadQueue.objects.filter(completed=False)
        for item in queue:
            print(f"downloading {item.episode.media_link}")
            item.download()
