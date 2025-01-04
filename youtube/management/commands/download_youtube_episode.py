from django.core.management.base import BaseCommand
from youtube.models import YoutubeEpisode


class Command(BaseCommand):
    help = "Test the Episode Download method"

    def handle(self, *args, **options):
        # Insert a mock episode
        episode = YoutubeEpisode(
            url="https://www.youtube.com/watch?v=EAx_RtMKPm8",
        )
        episode.save()

        # Test the download method
        episode.download()
        self.stdout.write(self.style.SUCCESS("Episode download method tested with mock episode"))
