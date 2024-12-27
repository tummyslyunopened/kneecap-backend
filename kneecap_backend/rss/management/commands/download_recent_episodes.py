from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from rss.models import Episode
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Downloads all episodes published in the last 24 hours'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Number of hours to look back (default: 24)'
        )

    def handle(self, *args, **options):
        hours = options['hours']
        cutoff_time = timezone.now() - timedelta(hours=hours)
        
        # Get episodes from last 24 hours that haven't been downloaded
        recent_episodes = Episode.objects.filter(
            pub_date__gte=cutoff_time,
            local_path__isnull=True,
            media__isnull=False
        )
        
        total_episodes = recent_episodes.count()
        self.stdout.write(f"Found {total_episodes} episodes to download")
        
        success_count = 0
        fail_count = 0
        
        for episode in recent_episodes:
            self.stdout.write(f"Downloading: {episode.title}")
            
            if episode.download():
                success_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f"Successfully downloaded: {episode.title}"
                ))
            else:
                fail_count += 1
                self.stdout.write(self.style.ERROR(
                    f"Failed to download: {episode.title}"
                ))
        
        # Final summary
        self.stdout.write("\nDownload Summary:")
        self.stdout.write(f"Total episodes: {total_episodes}")
        self.stdout.write(self.style.SUCCESS(f"Successfully downloaded: {success_count}"))
        if fail_count:
            self.stdout.write(self.style.ERROR(f"Failed downloads: {fail_count}")) 