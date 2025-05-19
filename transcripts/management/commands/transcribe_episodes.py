from django.core.management.base import BaseCommand
from subscriptions.models import Feed
from transcripts.service import generate_transcript
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.conf import settings


class Command(BaseCommand):
    help = "Generate Transcripts for Each Episode with local audio files"

    def handle(self, *args, **options):
        while True:
            episodes = (
                Feed.get_solo()
                .episodes.filter(audio_url__isnull=False, audio_url__gt="")
                .exclude(transcript_url__isnull=False, transcript_url__gt="")
                .order_by("duration")
            )

            # Create thread pool
            with ThreadPoolExecutor(max_workers=settings.TRANSCRIPTION_THREADS) as executor:
                # Submit all jobs to the executor
                futures = {executor.submit(generate_transcript, e): e for e in episodes}

                # Wait for all jobs to complete
                for future in as_completed(futures):
                    try:
                        future.result()  # This will raise any exceptions that occurred
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error processing episode: {str(e)}"))

            time.sleep(60)
