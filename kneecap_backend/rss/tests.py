from django.test import TestCase
from .models import RSSFeed, Episode

class RSSFeedTestCase(TestCase):

    def test_rssfeed_creation_logs(self):
        with self.assertLogs(level='INFO') as log:
            new_rss_feed = RSSFeed(link='https://www.omnycontent.com/d/playlist/e73c998e-6e60-432f-8610-ae210140c5b1/e7fd5ae7-7621-4e41-9b85-b0ab0164b634/4c1a5135-4197-47c9-b19b-b0ab0164b667/podcast.rss')# Example RSS feed link
            new_rss_feed.save()  # This should trigger the logging
        self.assertIn('Creating new RSSFeed:', log.output[0])  # Adjust the message as needed

    def setUp(self):
        # Create a sample RSS feed
        self.rss_feed = RSSFeed.objects.create(
            link='https://www.omnycontent.com/d/playlist/e73c998e-6e60-432f-8610-ae210140c5b1/e7fd5ae7-7621-4e41-9b85-b0ab0164b634/4c1a5135-4197-47c9-b19b-b0ab0164b667/podcast.rss',  # Example public RSS feed
        )

    def test_populate_episodes(self):
        # Call the method to populate episodes
        #with self.assertLogs(level='INFO') as log:
        self.rss_feed.populate_episodes()

        # Check if episodes were created
        episodes = Episode.objects.filter(rss_feed=self.rss_feed)
        self.assertGreater(episodes.count(), 0, "No episodes were created.")

        # Optionally, check the first episode's title and podcast URL
        first_episode = episodes.first()
        self.assertIsNotNone(first_episode.title, "The episode title should not be None.")
        self.assertIsNotNone(first_episode.podcast_url, "The podcast URL should not be None.")

    def test_no_duplicate_episodes(self):
        # Populate episodes the first time
        self.rss_feed.populate_episodes()
        initial_count = Episode.objects.filter(rss_feed=self.rss_feed).count()

        # Populate episodes again
        self.rss_feed.populate_episodes()
        new_count = Episode.objects.filter(rss_feed=self.rss_feed).count()

        # Ensure the count remains the same
        self.assertEqual(initial_count, new_count, "Duplicate episodes were created.")
