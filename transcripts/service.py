import requests
from django.conf import settings
import logging
import time
import os
import json
from subscriptions.models import Episode
from .models import TranscriptSegment

logger = logging.getLogger(__name__)


def start_transcription(audio_file_path):
    with open(audio_file_path, "rb") as audio_file:
        files = {"audio": audio_file}
        logger.info("\nStarting transcription process...")
        logger.info("This may take several minutes depending on the audio length.")
        logger.info("Uploading audio file...")

        try:
            response = requests.post(
                settings.TRANSCRIPTION_SERVICE_HOST + "/start",
                files=files,
                timeout=30,
            )

            if response.status_code != 200:
                logger.info(f"\nError: Failed to start transcription ({response.status_code})")
                logger.info("Response:", response.text)
                return None

            job_data = response.json()
            job_id = job_data.get("job_id")
            if not job_id:
                logger.info("\nError: No job ID received from server")
                return None

            logger.info(f"\nTranscription job started with ID: {job_id}")
            return job_id

        except requests.exceptions.RequestException as e:
            logger.info(f"\nError starting transcription: {str(e)}")
            return None


def poll_job_status(job_id, max_retries=120):
    status_url = settings.TRANSCRIPTION_SERVICE_HOST + f"/status/{job_id}"
    retry_count = 0

    while retry_count < max_retries:
        try:
            status_response = requests.get(status_url, timeout=30)

            if status_response.status_code == 200:
                status = status_response.json()
                if status.get("status") == "completed":
                    logger.info("\nTranscription completed successfully!")
                    return status
                elif status.get("status") == "failed":
                    logger.info("\nError: Transcription failed")
                    logger.info(f"Error details: {status.get('error', 'No error details')}")
                    return None

            logger.info(f"\rProgress: {retry_count}/{max_retries} retries")
            retry_count += 1
            time.sleep(5)

        except requests.exceptions.RequestException as e:
            logger.info(f"\nError during polling: {str(e)}")
            return None


def display_results(result):
    """Display the transcription results in a formatted way."""
    logger.info("\nTranscription:")
    logger.info("-" * 80)
    logger.info(result["transcription"])
    logger.info("-" * 80)
    logger.info(f"\nDetected Language: {result['language']}")
    logger.info("\nSegments with timestamps:")
    logger.info("-" * 80)
    for segment in result["segments"]:
        logger.info(f"[{segment['start']:.2f} - {segment['end']:.2f}]: {segment['text'].strip()}")


def save_transcript_json(episode: Episode, result):
    """Save the transcript result as JSON to the episode's transcript file path."""
    transcript_path = episode.derive_transcript_file_path
    if not transcript_path:
        logger.warning(f"No transcript file path for episode {episode.title}")
        return False

    try:
        # Get the directory path from the full file path
        dir_path = os.path.dirname(transcript_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(transcript_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving transcript to {transcript_path}: {str(e)}")
        return False


def create_transcript_segments(episode: Episode, result):
    """Load transcript segments into the database."""
    segments_to_add = [
        TranscriptSegment(
            episode=episode,
            start_time=segment["start"],
            end_time=segment["end"],
            text=segment["text"],
        )
        for segment in result["segments"]
    ]
    added_segments = TranscriptSegment.objects.bulk_create(segments_to_add)
    logger.info(f"{len(added_segments)} of {len(segments_to_add)} segments created")


def generate_transcript(episode: Episode):
    """Generate transcript for an episode and save both JSON and database records."""
    logger.info(f"Generating Transcript for episode {episode.title}")
    job_id = start_transcription(episode.derive_audio_file_path)
    if not job_id:
        return False
    logger.info("Polling for results...")
    result = poll_job_status(job_id)
    if not result:
        return False
    result = result["result"]
    if not save_transcript_json(episode, result):
        return False
    create_transcript_segments(episode, result)
    episode.transcript_url = episode.derive_transcript_url
    episode.save(update_fields=["transcript_url"])
    logger.info(f"Transcript generated for episode {episode.title}")
