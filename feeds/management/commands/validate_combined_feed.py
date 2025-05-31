from django.core.management.base import BaseCommand
from rss.parsers import parse_rss_entries
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Validate the combined RSS feed by parsing it and checking for missing fields.'

    def handle(self, *args, **kwargs):
        try:
            # Path to the combined feed
            combined_feed_path = os.path.join(settings.MEDIA_ROOT, 'feed/combined_feed.xml')

            if not os.path.exists(combined_feed_path):
                self.stderr.write(self.style.ERROR("Combined feed file does not exist."))
                return

            # Read the combined feed content
            with open(combined_feed_path, 'r', encoding='utf-8') as feed_file:
                feed_content = feed_file.read()

            # Parse the feed content
            success, entries = parse_rss_entries(feed_content)

            if not success:
                self.stderr.write(self.style.ERROR("Failed to parse the combined feed."))
                return

            # Output parsed entries to the console
            self.stdout.write(self.style.SUCCESS("Parsed Entries:"))
            for entry in entries:
                self.stdout.write(str(entry))

            # Check for missing fields in each entry
            for entry in entries:
                missing_fields = [
                    field for field in ["title", "pub_date", "description", "media_link"]
                    if not entry.get(field)
                ]
                if missing_fields:
                    self.stdout.write(
                        self.style.WARNING(f"Entry '{entry.get('title', 'Unknown')}' is missing fields: {', '.join(missing_fields)}")
                    )

            self.stdout.write(self.style.SUCCESS("Validation completed."))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred during validation: {e}"))
