import requests
from django.conf import settings
import os
import subprocess
import logging

logger = logging.getLogger(__name__)


def get_media_paths(link, uuid, media_path="unsorted", default_file_ext=""):
    try:
        base_url = link.split("?")[0]
        file_extension = os.path.splitext(base_url)[-1] or default_file_ext
        filename = f"{str(uuid)}{file_extension}"
        os.makedirs(os.path.join(settings.MEDIA_ROOT, media_path), exist_ok=True)
        file_path = os.path.join(media_path, filename)
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        url_path = (
            settings.SITE_URL.rstrip("/")
            + settings.MEDIA_URL.rstrip("/")
            + "/"
            + file_path.replace("\\", "/")
        )
        return full_path, url_path
    except Exception as e:
        logger.warn(f"Failed to generate media full_path and url_path: {e}")
        return ("", "")


def download_media_requests(link, uuid, media_path="unsorted", default_file_ext=""):
    full_path, url_path = get_media_paths(link, str(uuid), media_path, default_file_ext)
    try:
        response = requests.get(link, stream=True)
        response.raise_for_status()
        with open(full_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return (True, url_path)
    except Exception as e:
        logger.warn(f"failed to download media {e}")
        return (False, "")


def download_video_youtube_dl(
    link, uuid, media_path="unsorted", default_file_ext="", quality_code=""
):
    try:
        full_path, url_path = get_media_paths(
            link, uuid, media_path, default_file_ext, quality_code
        )
        command = f"youtube-dl --dateafter now-7days --playlist-end 2 --download-archive './downloaded.txt' -o './%(id)s.%(ext)s' -- '{link}'"
        subprocess.run(command, shell=True, check=True)
        return (True, url_path)
    except subprocess.CalledProcessError as e:
        logger.warn(f"Failed to download media at {link}: {e}")
        return (False, "")
