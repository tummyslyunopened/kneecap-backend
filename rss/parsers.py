from datetime import datetime, timedelta
import logging
import feedparser
from dateutil import parser

logger = logging.getLogger(__name__)


def parse_rss_entries(feed_content, days_cutoff=7):
    feed = feedparser.parse(feed_content)
    entries = []
    for entry in feed.entries:
        try:
            pub_date = parser.parse(entry.published, tzinfos=None)
            date_cutoff = datetime.now().replace(tzinfo=None) - timedelta(days=days_cutoff)
            if pub_date.replace(tzinfo=None) > date_cutoff.replace(tzinfo=None):
                duration = entry.get("itunes_duration", None)
                if duration:
                    parts = duration.split(":")
                    duration_in_seconds = 0
                    if len(parts) == 3:
                        h, m, s = map(int, parts)
                        duration_in_seconds = h * 3600 + m * 60 + s
                    elif len(parts) == 2:
                        m, s = map(int, parts)
                        duration_in_seconds = m * 60 + s
                    elif len(parts) == 1:
                        s = int(parts[0])
                        duration_in_seconds = s
                else:
                    duration_in_seconds = None
                entry_data = {
                    "title": entry.title,
                    "pub_date": pub_date.isoformat(),
                    "description": entry.description,
                    "duration": duration_in_seconds,
                    "media_link": entry.enclosures[0].url if entry.enclosures else None,
                }
                entries.append(entry_data)
        except Exception as e:
            logger.warn(f"failed to record data for entry {entry}: {e}")
    return (True, entries)


def parse_rss_feed_info(feed_content):
    feed = feedparser.parse(feed_content)
    return (
        feed.feed.title,
        feed.feed.description,
        feed.feed.image.href,
    )
