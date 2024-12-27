from django.db import models
import feedparser
from dateutil import parser
import logging
import requests
from django.utils import timezone
import uuid
import os
from django.conf import settings
from xml.etree import ElementTree as ET
# Set up logging
logger = logging.getLogger(__name__)

class RSSFeed(models.Model):
    title = models.CharField(max_length=500, default='')
    link = models.URLField()
    description = models.TextField(default='')
    pub_date = models.DateTimeField(auto_now_add=True)
    image = models.URLField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.title or not self.description:  # Check if title or description is missing
            feed = feedparser.parse(self.link)  # Parse the RSS feed
            self.title = feed.feed.title if not self.title else self.title
            self.description = feed.feed.description if not self.description else self.description
            self.image = feed.feed.image.href if hasattr(feed.feed, 'image') and hasattr(feed.feed.image, 'href') else self.image  # Get image URL
        
        # Log info when a new RSSFeed is created
        if self.pk is None:  # Check if the instance is being created
            logger.info(f"Creating new RSSFeed: Title: {self.title}")

        super().save(*args, **kwargs)

        # If this is a new feed, update the mirrored content
        if self.pk and not hasattr(self, 'mirror'):
            self.update_mirror()

    def update_mirror(self):
        """Downloads and stores the content from the external feed."""
        try:
            response = requests.get(self.link)
            response.raise_for_status()
            
            # Create or update the mirror
            mirror, created = FeedMirror.objects.get_or_create(
                rss_feed=self,
                defaults={'content': response.text}
            )
            if not created:
                mirror.content = response.text
                mirror.save()

            self.last_updated = timezone.now()
            self.save()
            
            logger.info(f"Successfully updated mirror for feed: {self.title}")
            return True

        except Exception as e:
            logger.error(f"Failed to update mirror for feed {self.title}: {str(e)}")
            return False

    def __str__(self):
        return self.title

    def populate_episodes(self):
        """Populate episodes using the mirrored content instead of fetching from the internet."""
        try:
            # Get the mirror content or return if none exists
            if not hasattr(self, 'mirror'):
                logger.warning(f"No mirror found for feed: {self.title}. Skipping episode population.")
                return

            feed = feedparser.parse(self.mirror.content)
            for entry in feed.entries:
                pub_date = parser.parse(entry.published)

                episode, created = Episode.objects.get_or_create(
                    rss_feed=self,
                    title=entry.title,
                    pub_date=pub_date,
                    defaults={
                        'description': entry.description,
                        'media': entry.enclosures[0].url if entry.enclosures else None
                    }
                )

                if created:
                    logger.info(f"Created episode: Title: {episode.title}, Published: {episode.pub_date}, Podcast URL: {episode.media}")
                else:
                    logger.info(f"Episode already exists: Title: {episode.title}, Published: {episode.pub_date}, Podcast URL: {episode.media}")

        except Exception as e:
            logger.error(f"Error populating episodes for feed {self.title}: {str(e)}")

class FeedMirror(models.Model):
    rss_feed = models.OneToOneField(RSSFeed, on_delete=models.CASCADE, related_name='mirror')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Mirror for {self.rss_feed.title}"

class StrippedMirror(models.Model):
    feed_mirror = models.OneToOneField(
        'FeedMirror',
        on_delete=models.CASCADE,
        related_name='stripped_mirror'
    )
    stripped_content = models.TextField(
        help_text="RSS content with only tracked parameters"
    )
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Stripped mirror for {self.feed_mirror}"

    def generate_stripped_content(self):
        """Generate stripped RSS content using only database model fields."""
        rss_feed = self.feed_mirror.rss_feed
        
        # Create a new RSS feed structure
        rss = ET.Element('rss', version='2.0')
        channel = ET.SubElement(rss, 'channel')
        
        # Add channel level elements from RSSFeed model
        title = ET.SubElement(channel, 'title')
        title.text = rss_feed.title
        
        link = ET.SubElement(channel, 'link')
        link.text = rss_feed.link
        
        description = ET.SubElement(channel, 'description')
        description.text = rss_feed.description
        
        # Add image if available
        if rss_feed.image:
            image = ET.SubElement(channel, 'image')
            image_url = ET.SubElement(image, 'url')
            image_url.text = rss_feed.image
            image_title = ET.SubElement(image, 'title')
            image_title.text = rss_feed.title
            image_link = ET.SubElement(image, 'link')
            image_link.text = rss_feed.link
        
        # Add items from Episode model
        for episode in rss_feed.episodes.all():
            item = ET.SubElement(channel, 'item')
            
            # Add title
            title = ET.SubElement(item, 'title')
            title.text = episode.title
            
            # Add description
            description = ET.SubElement(item, 'description')
            description.text = episode.description
            
            # Add guid
            guid = ET.SubElement(item, 'guid')
            guid.text = str(episode.guid)
            guid.set('isPermaLink', 'false')
            
            # Add pubDate
            pub_date = ET.SubElement(item, 'pubDate')
            pub_date.text = episode.pub_date.strftime('%a, %d %b %Y %H:%M:%S %z')
            
            # Add enclosure
            if episode.media or episode.local_path:
                enclosure = ET.SubElement(item, 'enclosure')
                # Update the enclosure URL to include the base URL for local paths
                enclosure.set('url', (settings.MEDIA_URL.rstrip('/') + episode.local_path) if episode.local_path else episode.media)
                enclosure.set('type', 'audio/mpeg')  # Default to audio/mpeg
                enclosure.set('length', '0')  # Default to 0 as we don't store file size
        
        # Convert to string with proper XML declaration and encoding
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(rss, encoding='unicode')

    def update(self):
        """Update the stripped content and save"""
        self.stripped_content = self.generate_stripped_content()
        self.save()

    class Meta:
        verbose_name = "Stripped Mirror"
        verbose_name_plural = "Stripped Mirrors"

class Episode(models.Model):
    rss_feed = models.ForeignKey(RSSFeed, related_name='episodes', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    pub_date = models.DateTimeField()
    media = models.URLField(max_length=200, blank=True, null=True)
    played = models.BooleanField(default=False)
    current_playback_time = models.DurationField(blank=True, null=True)
    guid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    local_path = models.URLField(max_length=500, null=True, blank=True)

    def download(self):
        """Downloads the episode media to local storage"""
        if not self.media:
            logger.warning(f"No media URL for episode: {self.title}")
            return False

        try:
            # Clean the URL to get just the base filename and extension
            base_url = self.media.split('?')[0]  # Remove query parameters
            file_extension = os.path.splitext(base_url)[-1] or '.mp3'  # Default to .mp3 if no extension
            filename = f"{self.guid}{file_extension}"
            
            # Download the file
            response = requests.get(self.media, stream=True)
            response.raise_for_status()
            
            # Ensure the media directory exists
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'episodes'), exist_ok=True)
            
            # Save the file
            file_path = os.path.join('episodes', filename)
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
            with open(full_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Store the URL path instead of file path
            url_path = settings.MEDIA_URL.rstrip('/') + '/' + file_path.replace('\\', '/')
            self.local_path = url_path
            self.save()
            
            logger.info(f"Successfully downloaded episode: {self.title}")
            return True

        except Exception as e:
            logger.error(f"Failed to download episode {self.title}: {str(e)}")
            return False

    def __str__(self):
        return self.title