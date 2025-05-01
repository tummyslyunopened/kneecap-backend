from typing import override
from django.core.management.base import BaseCommand
from subscriptions.models import Feed

from transcripts.service import generate_transcript
import time


class Command(BaseCommand):
    help = "Generate Transcripts for Each Episode with local audio files"

    @override
    def handle(self, *args, **options):
        while True:
            episodes = (
                Feed.get_solo()
                .episodes.filter(audio_url__isnull=False, audio_url__gt="")
                .exclude(transcript_url__isnull=False, transcript_url__gt="")
            )
            for e in episodes:
                generate_transcript(e)
            time.sleep(60)
