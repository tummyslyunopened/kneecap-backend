import time
from django.core.management.base import BaseCommand
from rss.models import RSSSubscription, RSSSubscriptionRefreshQueue


class Command(BaseCommand):
    help = "Create a RSSSubscriptionQueue for each RSSSubscription"

    def handle(self, *args, **options):
        while True:
            for subscription in RSSSubscription.objects.all():
                RSSSubscriptionRefreshQueue.objects.get_or_create(
                    subscription=subscription, completed=False
                )
            time.sleep(3600)  # Sleep for an hour before checking again