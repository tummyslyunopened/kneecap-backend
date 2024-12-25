from django.db import models
import feedparser
from dateutil import parser  # Import dateutil.parser
import logging

# Set up logging
logger = logging.getLogger(__name__)

class RSSFeed(models.Model):
    title = models.CharField(max_length=200, default='')
    link = models.URLField()
    description = models.TextField(default='')
    pub_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.title or not self.description:  # Check if title or description is missing
            feed = feedparser.parse(self.link)  # Parse the RSS feed
            self.title = feed.feed.title if not self.title else self.title  # Get title from feed
            self.description = feed.feed.description if not self.description else self.description  # Get description from feed
        
        # Log info when a new RSSFeed is created
        if self.pk is None:  # Check if the instance is being created
            logger.info(f"Creating new RSSFeed: Title: {self.title}, Link: {self.link}")

        super().save(*args, **kwargs)  # Call the original save method

    def __str__(self):
        return self.title

    def populate_episodes(self):
        feed = feedparser.parse(self.link)  # Parse the RSS feed
        for entry in feed.entries:
            # Use dateutil.parser to parse the published date
            pub_date = parser.parse(entry.published)

            # Check if the episode already exists
            episode, created = Episode.objects.get_or_create(
                rss_feed=self,
                title=entry.title,
                pub_date=pub_date,
                defaults={
                    'link': entry.link,
                    'description': entry.description,
                    'podcast_url': entry.enclosures[0].url if entry.enclosures else None
                }
            )

            if created:
                logger.info(f"Created episode: Title: {episode.title}, Link: {episode.link}, Published: {episode.pub_date}, Podcast URL: {episode.podcast_url}")
            else:
                logger.info(f"Episode already exists: Title: {episode.title}, Link: {episode.link}, Published: {episode.pub_date}, Podcast URL: {episode.podcast_url}")

class Episode(models.Model):
    rss_feed = models.ForeignKey(RSSFeed, related_name='episodes', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    link = models.URLField()
    description = models.TextField()
    pub_date = models.DateTimeField()
    podcast_url = models.URLField(max_length=200, blank=True, null=True)
    downloaded = models.BooleanField(default=False)  # Default to False
    played = models.BooleanField(default=False)      # Default to False
    current_playback_time = models.DurationField(blank=True, null=True)  # Optional field

    def __str__(self):
        return self.title