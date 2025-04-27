import unittest
from unittest.mock import patch
from django.conf import settings
from rss.models import RSSSubscription

# Patch model_instance_throttle before importing RSSSubscription
patcher = patch("rss.models.model_instance_throttle", lambda *a, **kw: (lambda f: f))
patcher.start()


class TestRSSSubscription(unittest.TestCase):
    def setUp(self):
        self.sub = RSSSubscription()
        self.sub.title = "Test Feed"
        self.sub.description = "Desc"
        self.sub.image_link = "http://img"
        self.sub.link = "http://feed"
        self.sub.uuid = "1234"
        self.sub.image_url = ""
        self.sub.rss_url = ""

    @patch("rss.models.parse_rss_feed_info")
    @patch.object(RSSSubscription, "download_image")
    @patch.object(RSSSubscription, "download_rss")
    def test_refresh(self, mock_download_rss, mock_download_image, mock_parse_info):
        mock_parse_info.return_value = ("Title", "Desc", "http://img")
        mock_download_image.return_value = (True, "/img.jpg")
        mock_download_rss.return_value = (True, "/rss.xml")
        self.sub.refresh()
        self.assertEqual(self.sub.title, "Title")
        self.assertEqual(self.sub.description, "Desc")
        self.assertEqual(self.sub.image_link, "http://img")
        mock_download_image.assert_called_once()
        mock_download_rss.assert_called_once()

    @patch("rss.models.download_media_requests")
    def test_download_image_success(self, mock_download):
        mock_download.return_value = (True, settings.SITE_URL.rstrip("/") + "/img.jpg")
        self.sub.image_link = "http://img"
        success, url = self.sub.download_image()
        self.assertTrue(success)
        self.assertEqual(url, "/img.jpg")

    @patch("rss.models.download_media_requests")
    def test_download_image_no_link(self, mock_download):
        self.sub.image_link = ""
        success, url = self.sub.download_image()
        self.assertFalse(success)
        self.assertEqual(url, "")
        mock_download.assert_not_called()

    @patch("rss.models.download_media_requests")
    def test_download_rss_success(self, mock_download):
        mock_download.return_value = (True, settings.SITE_URL.rstrip("/") + "/rss.xml")
        self.sub.link = "http://feed"
        success, url = self.sub.download_rss()
        self.assertTrue(success)
        self.assertEqual(url, "/rss.xml")

    @patch("rss.models.download_media_requests")
    def test_download_rss_no_link(self, mock_download):
        self.sub.link = ""
        success, url = self.sub.download_rss()
        self.assertFalse(success)
        self.assertEqual(url, "")
        mock_download.assert_not_called()

    def test_save_calls_refresh_if_title_empty(self):
        self.sub.title = ""
        with (
            patch.object(self.sub, "refresh") as mock_refresh,
            patch("django.db.models.Model.save") as mock_super_save,
        ):
            self.sub.save()
            mock_refresh.assert_called_once()
            mock_super_save.assert_called_once()

    def test_save_does_not_call_refresh_if_title_not_empty(self):
        self.sub.title = "not empty"
        with (
            patch.object(self.sub, "refresh") as mock_refresh,
            patch("django.db.models.Model.save") as mock_super_save,
        ):
            self.sub.save()
            mock_refresh.assert_not_called()
            mock_super_save.assert_called_once()


patcher.stop()
