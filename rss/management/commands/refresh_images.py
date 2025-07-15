from django.core.management.base import BaseCommand
from rss.models import RSSSubscription


class Command(BaseCommand):
    help = "Downloads missing media for all RSS subscriptions."

    def handle(self, *args, **options):
        subs = RSSSubscription.objects.all()
        for sub in subs:
            sub.download_image()
