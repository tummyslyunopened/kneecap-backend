from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from player.models import Player
from subscriptions.models import Episode, Subscription
from timeline.models import Minute


class TestTimelineView(TestCase):
    def setUp(self):
        self.client = Client()
        self.subscription = Subscription.objects.create(
            link="http://test.com/rss",
            title="Test Show",
            image_url="http://test.com/img.jpg",
        )
        self.episode = Episode.objects.create(
            subscription=self.subscription,
            title="Test Episode",
            pub_date=timezone.now(),
            playback_time=125,
        )
        player = Player.get_solo()
        player.episode = self.episode
        player.save()

    def test_timeline_renders_empty(self):
        response = self.client.get(reverse("timeline"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Timeline")
        self.assertContains(response, "No minutes recorded yet")

    def test_timeline_renders_recorded_minute(self):
        Minute.record()
        response = self.client.get(reverse("timeline"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Show")
        self.assertContains(response, "Test Episode")
        self.assertContains(response, "00:02:05")
