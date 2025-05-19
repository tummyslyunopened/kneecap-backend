import unittest
from datetime import timedelta
from django.utils import timezone
from subscriptions.models import Subscription, Episode, Feed
from django.db import IntegrityError
from django.test import TestCase


class SubscriptionModelTests(TestCase):
    def setUp(self):
        self.sub = Subscription.objects.create(link="http://test.com/rss")

    def test_recent_episode_none(self):
        self.assertIsNone(self.sub.recent_episode)

    def test_recent_episode_no_episodes(self):
        # Should hit the except block in recent_episode
        self.assertIsNone(self.sub.recent_episode)

    def test_recent_episode_with_episode(self):
        ep = Episode.objects.create(
            subscription=self.sub,
            title="Ep 1",
            description="desc",
            pub_date=timezone.now(),
        )
        self.assertEqual(self.sub.recent_episode, ep)
        self.assertEqual(self.sub.recent_episode_pub_date, ep.pub_date)

    def test_recent_episode_by_day_cuttoff(self):
        now = timezone.now()
        ep_recent = Episode.objects.create(
            subscription=self.sub,
            title="Recent",
            description="desc",
            pub_date=now - timedelta(days=3),
        )
        ep_old = Episode.objects.create(
            subscription=self.sub,
            title="Old",
            description="desc",
            pub_date=now - timedelta(days=10),
        )
        cutoff_episodes = self.sub.recent_episode_by_day_cuttoff
        self.assertIn(ep_recent, cutoff_episodes)
        self.assertNotIn(ep_old, cutoff_episodes)


class EpisodeModelTests(TestCase):
    def setUp(self):
        self.sub = Subscription.objects.create(
            link="http://test.com/rss", image_url="http://img.com/img.jpg"
        )

    def test_image_url(self):
        ep = Episode.objects.create(
            subscription=self.sub,
            title="Ep",
            description="desc",
            pub_date=timezone.now(),
        )
        self.assertEqual(ep.image_url, self.sub.image_url)

    def test_image_url_blank(self):
        sub2 = Subscription.objects.create(link="http://test2.com/rss", image_url="")
        ep = Episode.objects.create(
            subscription=sub2,
            title="Ep",
            description="desc",
            pub_date=timezone.now(),
        )
        self.assertEqual(ep.image_url, "")

    def test_unique_constraint(self):
        now = timezone.now()
        Episode.objects.create(
            subscription=self.sub,
            title="Ep",
            description="desc",
            pub_date=now,
        )
        with self.assertRaises(IntegrityError):
            Episode.objects.create(
                subscription=self.sub,
                title="Ep",
                description="desc",
                pub_date=now,
            )


class FeedModelTests(TestCase):
    def setUp(self):
        # Get or create the singleton Feed instance
        self.feed = Feed.get_solo()
        self.feed.chronological = True
        self.feed.cutoff_days = 7
        self.feed.save()

        self.sub = Subscription.objects.create(link="http://test.com/rss")
        self.now = timezone.now()

    def test_episodes_and_order_string_pref(self):
        ep1 = Episode.objects.create(
            subscription=self.sub,
            title="Ep1",
            description="desc",
            pub_date=self.now - timedelta(days=2),
        )
        ep2 = Episode.objects.create(
            subscription=self.sub,
            title="Ep2",
            description="desc",
            pub_date=self.now - timedelta(days=8),
        )
        episodes = self.feed.episodes
        self.assertIn(ep1, episodes)
        self.assertNotIn(ep2, episodes)
        self.assertEqual(self.feed.order_string_pref, "-")
        # Now test non-chronological branch
        self.feed.chronological = False
        self.feed.save()
        self.assertEqual(self.feed.order_string_pref, "")

    def test_episodes_view_hidden(self):
        # Hidden episode should be included if view_hidden is True
        ep_hidden = Episode.objects.create(
            subscription=self.sub,
            title="HiddenEp",
            description="desc",
            pub_date=self.now - timedelta(days=2),
            hidden=True,
        )
        self.feed.view_hidden = True
        self.feed.save()
        episodes = self.feed.episodes
        self.assertIn(ep_hidden, episodes)
        self.feed.view_hidden = False
        self.feed.save()
        episodes = self.feed.episodes
        self.assertNotIn(ep_hidden, episodes)


if __name__ == "__main__":
    unittest.main()
