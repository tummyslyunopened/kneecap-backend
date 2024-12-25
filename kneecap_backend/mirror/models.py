from django.db import models
from rss.models import RSSFeed
import requests
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class RSSMirror(models.Model):
    # mirror can be optionally associated with external rss feed, but is not necessary
    external_feed = models.ForeignKey(RSSFeed, related_name='mirror', null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=500, default='')
    external_feed_link = models.URLField(null=True)
    description = models.TextField(default='')
    pub_date = models.DateTimeField(auto_now_add=True)
    mirrored_content = models.TextField(blank=True)  # Store the mirrored XML content
    last_updated = models.DateTimeField(null=True)   # Track when the mirror was last updated

    def save(self, *args, update_mirror=True, **kwargs):
        """
        Override save to populate fields from external feed if they're not set
        and update the mirrored content.
        """
        if self.external_feed:
            # Copy over title and description if not set
            if not self.title:
                self.title = self.external_feed.title
            if not self.description:
                self.description = self.external_feed.description
            if not self.external_feed_link:
                self.external_feed_link = self.external_feed.link
            
        # Call the original save
        super().save(*args, **kwargs)
        
        # If this is a new mirror, update the content
        if update_mirror and self.external_feed and not self.mirrored_content:
            self.update_mirror()

    def update_mirror(self):
        """Downloads and stores the content from the external feed."""
        try:
            if not self.external_feed:
                logger.error(f"Mirror {self.id} has no associated external feed")
                return False

            response = requests.get(self.external_feed.link)
            response.raise_for_status()
            
            self.mirrored_content = response.text
            self.last_updated = timezone.now()
            self.save(update_mirror=False)  # Prevent infinite recursion
            
            logger.info(f"Successfully updated mirror {self.id} for feed {self.external_feed.title}")
            return True

        except Exception as e:
            logger.error(f"Failed to update mirror {self.id}: {str(e)}")
            return False

    def get_mirror_content(self):
        """Returns the mirrored content, updating it first if necessary."""
        if not self.last_updated or (timezone.now() - self.last_updated).days >= 1:
            self.update_mirror()
        return self.mirrored_content