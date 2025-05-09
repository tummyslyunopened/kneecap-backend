#!/bin/sh

# Create logs directory if it doesn't exist
mkdir -p ./logs

uv run manage.py makemigrations
uv run manage.py migrate

# Start each process in the background and redirect output and error to separate log files
uv run manage.py runserver 0.0.0.0:80 > ./logs/runserver-output.log 2> ./logs/runserver-error.log &
uv run manage.py sync_rss_data > ./logs/sync-rss-data-output.log 2> ./logs/sync-rss-data-error.log &
uv run manage.py download_media > ./logs/download-media-output.log 2> ./logs/download-media-error-log &
uv run manage.py transcribe_episodes > ./logs/transcribe-episodes-output.log 2> ./logs/transcribe-episodes-error-log &
uv run manage.py generate_low_quality > ./logs/generate-low-quality-output.log 2> ./logs/generate-low-quality-error.log &
uv run manage.py detect_ads> ./logs/detect-ads-output.log 2> ./logs/detect-ads-error.log &

# Use tail to follow the logs for each process
tail -f ./logs/runserver-output.log ./logs/runserver-error.log \
     ./logs/sync-rss-data-output.log ./logs/sync-rss-data-error.log \
     ./logs/download-media-output.log ./logs/download-media-error-log \
     ./logs/transcribe-episodes-output.log ./logs/transcribe-episodes-error-log \
     ./logs/generate-low-quality-output.log ./logs/generate-low-quality-error.log \
     ./logs/detect-ads-output.log ./logs/detect-ads-error.log

