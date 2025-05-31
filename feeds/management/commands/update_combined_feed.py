from django.core.management.base import BaseCommand
from feeds.generate import generate_combined_rss_feed

class Command(BaseCommand):
    help = 'Generate or update the combined RSS feed for all subscriptions.'

    def handle(self, *args, **kwargs):
        try:
            rss_file_path = generate_combined_rss_feed()
            self.stdout.write(self.style.SUCCESS(f"Combined RSS feed updated successfully: {rss_file_path}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to update combined RSS feed: {e}"))
