import unittest
from rss import parsers
import os


class TestParseRssEntries(unittest.TestCase):
    def test_parser(self):
        # Test parse_rss_entries using sample_feed.xml from disk (new signature: content, not url)
        sample_path = os.path.join(os.path.dirname(__file__), "sample_feed.xml")
        with open(sample_path, "r", encoding="utf-8") as f:
            sample_content = f.read()
            ok, entries = parsers.parse_rss_entries(sample_content)
            print(entries)
            self.assertTrue(isinstance(ok, bool))
            self.assertTrue(isinstance(entries, list))
            # Check itunes:duration is parsed for Episode 1
            ep1 = next(e for e in entries if e["title"] == "Episode 1")
            self.assertEqual(ep1["duration"], 3723)  # 1:02:03 = 3723 seconds
            # Check MM:SS duration
            ep_mmss = next(e for e in entries if e["title"] == "Episode MMSS")
            self.assertEqual(ep_mmss["duration"], 123)  # 2:03 = 123 seconds
            # Check SS duration
            ep_ss = next(e for e in entries if e["title"] == "Episode SS")
            self.assertEqual(ep_ss["duration"], 42)  # 42 seconds
            # Check malformed duration is handled (should be skipped)
            self.assertFalse(any(e["title"] == "Episode Bad" for e in entries))

    def test_parser_invalid_xml(self):
        # This should NOT raise, feedparser returns ok=True and entries=[]
        ok, entries = parsers.parse_rss_entries("not xml")
        self.assertTrue(ok)
        self.assertEqual(entries, [])


class TestParseRssFeedInfo(unittest.TestCase):
    def test_feed_info_valid(self):
        sample_path = os.path.join(os.path.dirname(__file__), "sample_feed.xml")
        with open(sample_path, "r", encoding="utf-8") as f:
            sample_content = f.read()
        title, desc, img = parsers.parse_rss_feed_info(sample_content)
        self.assertEqual(title, "Sample Podcast")
        self.assertEqual(desc, "Desc")
        self.assertEqual(img, "http://img")

    def test_feed_info_missing_title(self):
        malformed = """<rss><channel><description>Desc</description><image><url>http://img</url></image></channel></rss>"""
        with self.assertRaises(AttributeError):
            parsers.parse_rss_feed_info(malformed)

    def test_feed_info_missing_image(self):
        malformed = """<rss><channel><title>Sample Podcast</title><description>Desc</description></channel></rss>"""
        with self.assertRaises(AttributeError):
            parsers.parse_rss_feed_info(malformed)

    def test_feed_info_invalid_xml(self):
        malformed = "<rss><channel><title>Sample Podcast</title><description>Desc</description>"  # No closing tags
        with self.assertRaises(Exception):
            parsers.parse_rss_feed_info(malformed)
