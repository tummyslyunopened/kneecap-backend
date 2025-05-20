import requests
import time
from django.core.management.base import BaseCommand
from django.conf import settings
from requests.exceptions import RequestException


class Command(BaseCommand):
    help = "Test transcription service with provided audio file"

    def add_arguments(self, parser):
        parser.add_argument("audio_file", type=str, help="Path to the audio file to transcribe")

    def start_transcription(self, audio_file_path):
        with open(audio_file_path, "rb") as audio_file:
            files = {"audio": audio_file}
            print("\nStarting transcription process...")
            print("This may take several minutes depending on the audio length.")
            print("Uploading audio file...")

            try:
                response = requests.post(
                    settings.TRANSCRIPTION_SERVICE_HOST + "/start",
                    files=files,
                    timeout=30,
                )

                if response.status_code != 200:
                    print(f"\nError: Failed to start transcription ({response.status_code})")
                    print("Response:", response.text)
                    return None

                job_data = response.json()
                job_id = job_data.get("job_id")
                if not job_id:
                    print("\nError: No job ID received from server")
                    return None

                print(f"\nTranscription job started with ID: {job_id}")
                return job_id

            except RequestException as e:
                print(f"\nError starting transcription: {str(e)}")
                return None

    def poll_job_status(self, job_id, max_retries=120):
        status_url = settings.TRANSCRIPTION_SERVICE_HOST + f"/status/{job_id}"
        retry_count = 0

        while retry_count < max_retries:
            try:
                status_response = requests.get(status_url, timeout=30)

                if status_response.status_code == 200:
                    status = status_response.json()
                    if status.get("status") == "completed":
                        print("\nTranscription completed successfully!")
                        return status
                    elif status.get("status") == "failed":
                        print("\nError: Transcription failed")
                        print("Error details:", status.get("error", "No error details"))
                        return None

                print(f"\rProgress: {retry_count}/{max_retries} retries", end="")
                retry_count += 1
                time.sleep(5)

            except RequestException as e:
                print(f"\nError during polling: {str(e)}")
                return None

    def display_results(self, result):
        result = result["result"]
        """Display the transcription results in a formatted way."""
        print("\nTranscription:")
        print("-" * 80)
        print(result["transcription"])
        print("-" * 80)
        print(f"\nDetected Language: {result['language']}")
        print("\nSegments with timestamps:")
        print("-" * 80)
        for segment in result["segments"]:
            print(f"[{segment['start']:.2f} - {segment['end']:.2f}]: {segment['text'].strip()}")

    def handle(self, *args, **options):
        """Main command handler that orchestrates the transcription process."""
        audio_file_path = options["audio_file"]

        # Start the transcription job
        job_id = self.start_transcription(audio_file_path)
        if not job_id:
            return

        # Poll for job status
        print("Polling for results...")
        result = self.poll_job_status(job_id)
        if not result:
            return

        # Display the results
        self.display_results(result)
