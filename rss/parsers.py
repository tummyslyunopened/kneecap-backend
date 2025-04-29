from datetime import datetime, timedelta
import logging
from django.conf import settings
import feedparser
from dateutil import parser
from reader import make_reader

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


def parse_rss_entries_reader(feed_url, days_cutoff=7):
    """
    Fetch and parse RSS entries using lemon24/reader library.
    Args:
        feed_url (str): The URL of the RSS/Atom feed.
        days_cutoff (int): Only include entries newer than this number of days.
    Returns:
        (bool, list): (success, entries) tuple
    """
    try:
        with make_reader(settings.READER_DB_PATH) as r:
            # Always try to add the feed before updating/fetching
            try:
                r.add_feed(feed_url)
            except Exception as e:
                # Log but ignore errors if feed already exists
                logger.info(f"add_feed: {e}")
            r.update_feeds()
            entries = []
            date_cutoff = datetime.now().replace(tzinfo=None) - timedelta(days=days_cutoff)
            for entry in r.get_entries(feed=feed_url, read=False, limit=3):
                pub_date = entry.published or entry.updated or entry.added
                if pub_date and pub_date.replace(tzinfo=None) > date_cutoff.replace(tzinfo=None):
                    duration = (
                        entry.enclosure_length if hasattr(entry, "enclosure_length") else None
                    )
                    entry_data = {
                        "title": entry.title,
                        "pub_date": pub_date.isoformat(),
                        "description": getattr(entry, "summary", ""),
                        "duration": duration,
                        "media_link": entry.enclosure_href
                        if hasattr(entry, "enclosure_href")
                        else None,
                    }
                    entries.append(entry_data)
        return (True, entries)
    except Exception as e:
        logger.warn(f"Failed to fetch/parse with reader: {e}")
        return (False, [])


def parse_rss_feed_info_reader(feed_url):
    """
    Fetch and parse RSS feed info using lemon24/reader library.
    Returns (title, description, image_link) or falls back to feedparser if NonXMLContentType error occurs.
    """
    try:
        with make_reader(settings.READER_DB_PATH) as r:
            # Always try to add the feed before updating/fetching
            try:
                r.add_feed(feed_url)
            except Exception as e:
                logger.info(f"add_feed: {e}")
            r.update_feeds()
            f = r.get_feed(feed_url)
            if not f:
                raise Exception(f"No such feed: {feed_url}")
            title = f.title or ""
            description = f.description or ""
            image_link = None
            if hasattr(f, "image") and f.image and hasattr(f.image, "href"):
                image_link = f.image.href
            return (title, description, image_link)
    except Exception as e:
        logger.warning(f"Failed to fetch feed info with reader: {e}")
        return parse_rss_feed_info(feed_url)[0:2]
