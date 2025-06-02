from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from timeline.models import Minute
from player.models import Player
from subscriptions.models import Episode, Subscription
from unittest.mock import patch


class TestMinuteModel(TestCase):
    def setUp(self):
        # Get the Player singleton
        self.player = Player.get_solo()
        
        # Create a test subscription
        self.subscription = Subscription.objects.create(
            link="http://test.com/rss"
        )
        
        # Create a test episode
        self.test_episode = Episode.objects.create(
            subscription=self.subscription,
            title="Test Episode", 
            pub_date=timezone.now(), 
            playback_time=1800  # 30 minutes in seconds
        )

    def test_record_with_active_episode(self):
        """Test recording a minute when there is an active episode"""
        # Set up player with an active episode
        self.player.episode = self.test_episode
        self.player.save()

        # Record a minute
        minute = Minute.record()

        # Verify the minute was recorded
        self.assertIsNotNone(minute)
        self.assertEqual(minute.episode, self.test_episode)
        self.assertEqual(minute.playback_time, self.test_episode.playback_time)

    def test_record_without_active_episode(self):
        """Test recording a minute when there is no active episode"""
        # Ensure no active episode
        self.player.episode = None
        self.player.save()

        # Try to record a minute
        minute = Minute.record()

        # Verify no minute was recorded
        self.assertIsNone(minute)

    def test_record_duplicate_minute(self):
        """Test that recording the same minute twice returns None for the second attempt"""
        # Set up player with an active episode
        self.player.episode = self.test_episode
        self.player.save()

        # Record first minute
        first_minute = Minute.record()
        self.assertIsNotNone(first_minute)

        # Try to record another minute immediately (should return None as same minute)
        second_minute = Minute.record()
        self.assertIsNone(second_minute)

    def test_record_different_minutes(self):
        """Test recording different minutes works correctly"""
        # Set up player with an active episode
        self.player.episode = self.test_episode
        self.player.save()

        # Record first minute
        first_minute = Minute.record()
        self.assertIsNotNone(first_minute)

        # Mock timezone.now() to return a different minute
        future_time = timezone.now() + timedelta(minutes=1)
        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = future_time
            second_minute = Minute.record()
            self.assertIsNotNone(second_minute)
            self.assertNotEqual(first_minute.created_at, second_minute.created_at)

    def test_minute_image_property(self):
        """Test the image property of the Minute model"""
        # Set up player with an active episode
        self.player.episode = self.test_episode
        self.player.save()        # Set an image URL for the subscription
        test_image = "test_image.jpg"
        self.subscription.image_url = test_image
        self.subscription.save()

        # Record a minute
        minute = Minute.record()

        # Verify the minute's image property returns the episode's image URL
        self.assertEqual(minute.image, test_image)
