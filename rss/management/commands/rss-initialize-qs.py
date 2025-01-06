from django.core.management.base import BaseCommand
from rss.models import RSSSubscription, RSSSubscriptionRefreshQueue


class Command(BaseCommand):
    help = "Create a RSSSubscriptionQueue for each RSSSubscription"

    def handle(self, *args, **options):
        for subscription in RSSSubscription.objects.all():
            RSSSubscriptionRefreshQueue.objects.get_or_create(
                subscription=subscription, completed=False
            )
