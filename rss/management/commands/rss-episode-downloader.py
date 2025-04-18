from django.core.management.base import BaseCommand
from rss.models import RSSEpisodeDownloadQueue
import time  


class Command(BaseCommand):
    help = "Download RSS Episode Audio Content"

    def handle(self, *args, **options):
        while True:
            delay = 10 
            min_delay = 1
            max_delay = 180
            queue = RSSEpisodeDownloadQueue.objects.filter(completed=False)
            for item in queue:
                print(f"downloading {item.episode.media_link}")
                if not item.download():  # Assuming download() returns False on failure
                    delay = min(delay * 2, max_delay)
                    print(f"Failed to download, increasing delay to {delay}")
                else:
                    delay = max(min_delay / 2, 1)
                    print(f"Successful, decreasing delay to {delay}")
                time.sleep(delay)  # Delay before the next download attempt