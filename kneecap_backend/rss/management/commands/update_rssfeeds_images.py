from django.core.management.base import BaseCommand
from rss.models import RSSFeed
import feedparser
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Updates the image URLs for all RSS feeds'

    def handle(self, *args, **kwargs):
        feeds = RSSFeed.objects.all()
        for feed in feeds:
            try:
                # Parse the feed to get the latest image URL
                parsed_feed = feedparser.parse(feed.link)
                new_image = parsed_feed.feed.image.href if hasattr(parsed_feed.feed, 'image') and hasattr(parsed_feed.feed.image, 'href') else None
                
                if new_image and new_image != feed.image:
                    feed.image = new_image
                    feed.save()
                    logger.info(f"Updated image for RSSFeed: {feed.title}")
                else:
                    logger.info(f"No update needed for RSSFeed: {feed.title}")

            except Exception as e:
                logger.error(f"Error updating image for RSSFeed {feed.title}: {str(e)}")