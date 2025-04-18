from django.core.management.base import BaseCommand
from rss.models import RSSSubscriptionRefreshQueue
import time

class Command(BaseCommand):
    help = "Refresh RSS subscriptions"

    def handle(self, *args, **options):
        while True:
            queue = RSSSubscriptionRefreshQueue.objects.filter(completed=False)
            delay = 10 
            min_delay = 1
            max_delay = 180
            for item in queue:
                print(f"Attempting to refresh subscription: {item.subscription.title} ")
                if not item.refresh():
                    delay = min(delay * 2, max_delay)
                    print(f"Failed to refresh, increasing delay to {delay}")
                else: 
                    delay = max(min_delay / 2 , 1)
                    print(f"Successful, decreasing delay to {delay}")
                time.sleep(delay) 