from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock
import requests
from rss.models import RSSFeed
from .models import RSSMirror
import xml.etree.ElementTree as ET

class RSSMirrorModelTests(TestCase):
    def setUp(self):
        self.feed = RSSFeed.objects.create(
            title="99% Invisible",
            link="https://feeds.simplecast.com/BqbsxVfO",
            description="Design is everywhere in our lives, perhaps most importantly in the places where we've just stopped noticing."
        )

    def test_mirror_creation_from_feed(self):
        """Test that mirror copies feed metadata correctly"""
        mirror = RSSMirror(external_feed=self.feed)
        mirror.save(update_mirror=False)
        
        self.assertEqual(mirror.title, self.feed.title)
        self.assertEqual(mirror.external_feed_link, self.feed.link)
        self.assertEqual(mirror.description, self.feed.description)

    @patch('requests.get')
    def test_update_mirror_failure(self, mock_get):
        """Test handling of network errors during update"""
        mock_get.side_effect = requests.RequestException("Network error")

        mirror = RSSMirror(external_feed=self.feed)
        mirror.save(update_mirror=False)
        success = mirror.update_mirror()

        self.assertFalse(success)
        self.assertEqual(mirror.mirrored_content, "")

    def test_get_mirror_content_updates_old_content(self):
        """Test that get_mirror_content triggers update for old content"""
        mirror = RSSMirror(
            external_feed=self.feed,
            mirrored_content="old content",
            last_updated=timezone.now() - timedelta(days=2)
        )
        mirror.save(update_mirror=False)

        with patch.object(mirror, 'update_mirror') as mock_update:
            mirror.get_mirror_content()
            mock_update.assert_called_once()

    def test_mirror_without_feed(self):
        """Test that mirror can exist without external feed"""
        mirror = RSSMirror(
            title="Standalone Mirror",
            description="No external feed"
        )
        mirror.save(update_mirror=False)
        
        self.assertIsNone(mirror.external_feed)
        self.assertEqual(mirror.title, "Standalone Mirror")

class RSSMirrorViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.feed = RSSFeed.objects.create(
            title="99% Invisible",
            link="https://feeds.simplecast.com/BqbsxVfO",
            description="Design is everywhere in our lives, perhaps most importantly in the places where we've just stopped noticing."
        )
        
        self.mirror = RSSMirror(
            external_feed=self.feed,
        )
        self.mirror.save(update_mirror=True)

    def test_serve_mirror_returns_xml(self):
        """Test that served content is valid XML with correct content type"""
        url = reverse('mirror:serve_mirror', args=[self.mirror.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')
        
        # Verify the response is valid XML
        try:
            root = ET.fromstring(response.content)
            self.assertEqual(root.tag, 'rss')
            self.assertIn('version', root.attrib)
        except ET.ParseError:
            self.fail("Response is not valid XML")

    def test_serve_mirror_content_matches(self):
        """Test that served content matches stored content structure"""
        url = reverse('mirror:serve_mirror', args=[self.mirror.id])
        response = self.client.get(url)
        
        # Parse both stored and served XML
        stored_xml = ET.fromstring(self.mirror.mirrored_content)
        served_xml = ET.fromstring(response.content.decode())
        
        # Compare basic structure
        self.assertEqual(served_xml.tag, stored_xml.tag)
        self.assertEqual(served_xml.attrib.get('version'), stored_xml.attrib.get('version'))

    def test_serve_mirror_404(self):
        """Test 404 response for non-existent mirror"""
        url = reverse('mirror:serve_mirror', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

