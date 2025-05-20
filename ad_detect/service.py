import requests
import json
from typing import List, Dict, Tuple
import logging
from pathlib import Path
from requests.exceptions import RequestException
from transcripts.models import TranscriptSegment
from kneecap.settings import LLM_ENDPOINT

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
DEFAULT_BATCH_SIZE = 20
DEFAULT_API_URL = LLM_ENDPOINT


class BaseTranscriptSegment:
    """Base class for transcript segment types."""

    def __init__(self, text: str, advertising_detected: bool = False):
        self.text = text
        self.advertising_detected = advertising_detected

    def mark_as_ad(self):
        """Mark this segment as containing advertising content."""
        self.advertising_detected = True


class JsonTranscriptSegment(BaseTranscriptSegment):
    """Transcript segment loaded from JSON file."""

    def __init__(self, data: Dict):
        super().__init__(data.get("text", ""), data.get("advertising_detected", False))
        self.data = data

    def mark_as_ad(self):
        super().mark_as_ad()
        self.data["advertising_detected"] = True


class DatabaseTranscriptSegment(BaseTranscriptSegment):
    """Transcript segment loaded from database."""

    def __init__(self, segment: TranscriptSegment):
        super().__init__(segment.text, segment.ai_detected_advertising)
        self.segment = segment
        self.reviewed = segment.ai_advertising_reviewed

    def mark_as_ad(self):
        super().mark_as_ad()
        self.segment.ai_detected_advertising = True
        self.segment.ai_advertising_reviewed = True
        self.segment.save()

    def mark_as_reviewed(self):
        """Mark this segment as having been reviewed for advertising."""
        self.reviewed = True
        self.segment.ai_advertising_reviewed = True
        self.segment.save()


class AdDetectionConfig:
    """Configuration for ad detection service."""

    def __init__(self, api_url: str = DEFAULT_API_URL, batch_size: int = DEFAULT_BATCH_SIZE):
        self.api_url = api_url
        self.batch_size = batch_size


class AdDetectionService:
    """Service for detecting advertisements in transcript segments."""

    def __init__(self, config: AdDetectionConfig):
        self.config = config
        self.headers = {"Content-Type": "application/json"}

    def _prepare_payload(self, batch_text: str) -> Dict:
        """Prepare the payload for API request."""
        return {
            "messages": [
                {
                    "role": "system",
                    "content": "Determine if the excerpt contains any sponsored or advertising content.",
                },
                {"role": "system", "content": "Respond only with True or False."},
                {"role": "user", "content": batch_text},
            ],
            "temperature": 0.7,
            "max_tokens": 10,
            "stream": False,
        }

    def _process_batch(self, batch: List[BaseTranscriptSegment]) -> Tuple[bool, bool]:
        """Process a single batch of segments."""
        batch_text = " ".join(segment.text for segment in batch)
        payload = self._prepare_payload(batch_text)
        success = False
        ad_detected = False

        try:
            response = requests.post(self.config.api_url, json=payload, headers=self.headers)

            if response.status_code == 200:
                response_data = response.json()
                success = True
                ad_detected = self._is_ad_response(response_data)
            else:
                logger.error(
                    f"Failed to get response. Status code: {response.status_code}, Error: {response.text}"
                )

        except RequestException as e:
            logger.error(f"Request failed: {str(e)}")

        return success, ad_detected

    def _is_ad_response(self, response_data: Dict) -> bool:
        """Check if response indicates advertising content."""
        return (
            "choices" in response_data
            and response_data["choices"][0]["message"]["content"].strip().lower() == "true"
        )

    def detect_ads(
        self, transcript_segments: List[BaseTranscriptSegment]
    ) -> List[BaseTranscriptSegment]:
        """Detect ads in transcript segments."""
        processed_segments = transcript_segments.copy()
        for i in range(0, len(processed_segments), self.config.batch_size):
            batch = processed_segments[i : i + self.config.batch_size]
            success, ad_detected = self._process_batch(batch)
            for segment in batch:
                if success:
                    if ad_detected:
                        segment.mark_as_ad()
                    segment.mark_as_reviewed()

        return processed_segments


def load_transcript_from_json(file_path: str) -> List[JsonTranscriptSegment]:
    """Load transcript segments from JSON file."""
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            return [JsonTranscriptSegment(segment) for segment in data["segments"]]
    except FileNotFoundError:
        logger.error(f"File {file_path} not found.")
        raise
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON from {file_path}")
        raise


def get_segments_for_episode(
    episode_id: int, reviewed: bool = False
) -> List[DatabaseTranscriptSegment]:
    """Get transcript segments for a specific episode.

    Args:
        episode_id: ID of the episode to get segments for
        reviewed: If True, only return reviewed segments; if False, only return unreviewed
    """
    try:
        segments = TranscriptSegment.objects.filter(episode_id=episode_id)
        if reviewed:
            segments = segments.filter(ai_advertising_reviewed=True)
        else:
            segments = segments.filter(ai_advertising_reviewed=False)
        return [DatabaseTranscriptSegment(segment) for segment in segments]
    except Exception as e:
        logger.error(f"Error retrieving segments for episode {episode_id}: {str(e)}")
        raise


def get_unreviewed_segments() -> List[DatabaseTranscriptSegment]:
    """Get all transcript segments that haven't been reviewed for advertising."""
    try:
        segments = TranscriptSegment.objects.filter(ai_advertising_reviewed=False)
        return [DatabaseTranscriptSegment(segment) for segment in segments]
    except Exception as e:
        logger.error(f"Error retrieving unreviewed segments: {str(e)}")
        raise


def save_json_transcript(segments: List[JsonTranscriptSegment], output_path: str) -> None:
    """Save processed transcript segments to JSON file."""
    try:
        data = {"segments": [segment.data for segment in segments]}
        with open(output_path, "w") as file:
            json.dump(data, file, indent=4)
    except IOError as e:
        logger.error(f"Error saving processed transcript: {str(e)}")
        raise


def get_processed_file_path(input_path: str) -> str:
    """Generate processed file path by adding '_processed' suffix."""
    path = Path(input_path)
    return str(path.with_stem(f"{path.stem}_processed"))
