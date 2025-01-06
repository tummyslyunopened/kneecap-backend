from django.core.management.base import BaseCommand
from rss.models import RSSSubscriptionRefreshQueue


class Command(BaseCommand):
    help = "Refresh RSS subscriptions"

    def handle(self, *args, **options):
        queue = RSSSubscriptionRefreshQueue.objects.filter(completed=False)
        for item in queue:
            item.refresh()
