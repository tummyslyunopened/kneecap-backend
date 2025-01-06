import requests
import feedparser
from dateutil import parser
from datetime import datetime, timedelta
import logging
# from icecream import ic

logger = logging.getLogger(__name__)


def parse_rss_entries(link, entry_url_field_name="url", days_cutoff=7):
    try:
        feed_content = requests.get(url=link).content
        feed = feedparser.parse(feed_content)
        entries = []
        for entry in feed.entries:
            try:
                pub_date = parser.parse(entry.published, tzinfos=None)
                date_cutoff = datetime.now().replace(tzinfo=None) - timedelta(days=days_cutoff)
                if pub_date.replace(tzinfo=None) > date_cutoff.replace(tzinfo=None):
                    entry_data = {
                        "title": entry.title,
                        "pub_date": pub_date.isoformat(),
                        "description": entry.description,
                        entry_url_field_name: entry.enclosures[0].url
                        if entry.enclosures
                        else None,
                    }
                    entries.append(entry_data)
            except Exception as e:
                logger.warn(f"failed to record data for entry {entry}: {e}")
        return (True, entries)

    except Exception as e:
        logger.warn(f"failed to parse rss Feed at link {link}: {e}")
        return (False, [])


def parse_rss_feed_info(link):
    feed = feedparser.parse(link)
    return (
        feed.feed.title,
        feed.feed.description,
        feed.feed.image.href,
    )
