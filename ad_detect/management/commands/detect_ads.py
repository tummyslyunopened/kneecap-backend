from typing import override
from django.core.management.base import BaseCommand
import time
from ad_detect.service import AdDetectionConfig, AdDetectionService, get_unreviewed_segments


class Command(BaseCommand):
    help = "Generate Transcripts for Each Episode with local audio files"

    @override
    def handle(self, *args, **options):
        while True:
            config = AdDetectionConfig()
            transcript_segments = get_unreviewed_segments()
            # Initialize service and process transcript
            service = AdDetectionService(config)
            service.detect_ads(transcript_segments)
            time.sleep(60)
