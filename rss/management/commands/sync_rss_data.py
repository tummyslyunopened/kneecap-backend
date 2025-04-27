from django.core.management.base import BaseCommand
from rss.models import RSSSubscription


class Command(BaseCommand):
    help = "Refreshes all RSS subscriptions."

    def handle(self, *args, **options):
        while True:
            for subscription in RSSSubscription.objects.all():
                subscription.refresh()
                subscription.populate_recent_episodes()
                for episode in subscription.episodes.filter(audio_url=""):
                    RSSSubscription.download_episode_audio(episode)
