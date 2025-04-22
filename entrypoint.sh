#!/bin/sh

# Create logs directory if it doesn't exist
mkdir -p ./logs

uv sync 
uv run makemigrations
uv run migrate

# Start each process in the background and redirect output and error to separate log files
uv run manage.py runserver 0.0.0.0:80 > ./logs/runserver-output.log 2> ./logs/runserver-error.log &
uv run manage.py rss-episode-downloader > ./logs/rss-episode-downloader-output.log 2> ./logs/rss-episode-downloader-error.log &
uv run manage.py rss-subscriptions-refresher > ./logs/rss-subscriptions-refresher-output.log 2> ./logs/rss-subscriptions-refresher-error.log &
uv run manage.py rss-q-subscriptions > ./logs/rss-q-subscriptions-output.log 2> ./logs/rss-q-subscriptions-error.log &

# Use tail to follow the logs for each process
tail -f ./logs/runserver-output.log ./logs/runserver-error.log \
     ./logs/rss-episode-downloader-output.log ./logs/rss-episode-downloader-error.log \
     ./logs/rss-subscriptions-refresher-output.log ./logs/rss-subscriptions-refresher-error.log \
     ./logs/rss-q-subscriptions-output.log ./logs/rss-q-subscriptions-error.log
