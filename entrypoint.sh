#!/bin/sh
# Start each process and redirect output to log files
uv run manage.py runserver 0.0.0.0:80 > runserver.log 2>&1 & \
uv run manage.py rss-episode-downloader > rss-episode-downloader.log 2>&1 & \
uv run manage.py rss-subscriptions-refresher > rss-subscriptions-refresher.log 2>&1 &

# Use tail to follow the logs
tail -f runserver.log rss-episode-downloader.log rss-subscriptions-refresher.log
