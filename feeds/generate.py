import os
from xml.etree.ElementTree import Element, SubElement, ElementTree
from subscriptions.models import Subscription
from django.conf import settings
from tqdm import tqdm


def generate_rss_feed(subscription_id):
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        episodes = subscription.episodes.all()

        # Create the root element
        rss = Element(
            "rss",
            version="2.0",
            attrib={"xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"},
        )
        channel = SubElement(rss, "channel")

        # Add subscription-level details
        SubElement(channel, "title").text = subscription.title
        SubElement(channel, "link").text = subscription.link
        SubElement(channel, "description").text = subscription.description
        SubElement(channel, "language").text = "en-us"  # Default language
        SubElement(channel, "itunes:image", href=subscription.image_url)

        # Add episodes
        for episode in episodes:
            item = SubElement(channel, "item")
            SubElement(item, "title").text = episode.title
            SubElement(item, "description").text = episode.description
            SubElement(item, "pubDate").text = episode.pub_date.strftime(
                "%a, %d %b %Y %H:%M:%S %z"
            )
            SubElement(item, "guid").text = str(episode.uuid)
            audio_url = episode.audio_url if episode.audio_url else episode.media_link
            SubElement(item, "enclosure", attrib={"url": audio_url, "type": "audio/mpeg"})
            SubElement(item, "itunes:duration").text = episode.duration_str

        # Write to file
        rss_file_path = os.path.join(settings.MEDIA_ROOT, f"rss/{subscription_id}.xml")
        os.makedirs(os.path.dirname(rss_file_path), exist_ok=True)
        tree = ElementTree(rss)
        tree.write(rss_file_path, encoding="utf-8", xml_declaration=True)

        return rss_file_path

    except Subscription.DoesNotExist:
        raise ValueError(f"Subscription with id {subscription_id} does not exist.")
    except Exception as e:
        raise RuntimeError(f"Failed to generate RSS feed: {e}")


def generate_combined_rss_feed():
    try:
        subscriptions = Subscription.objects.all()

        # Create the root element
        rss = Element(
            "rss",
            version="2.0",
            attrib={"xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"},
        )
        channel = SubElement(rss, "channel")

        # Add combined feed-level details
        SubElement(channel, "title").text = "Combined Podcast Feed"
        SubElement(channel, "link").text = "https://example.com/combined-feed"
        SubElement(channel, "description").text = "A combined feed of all subscriptions."
        SubElement(channel, "language").text = "en-us"  # Default language

        # Add episodes from all subscriptions with a progress bar
        total_episodes = sum(subscription.episodes.count() for subscription in subscriptions)
        with tqdm(total=total_episodes, desc="Generating Combined RSS Feed") as pbar:
            for subscription in subscriptions:
                episodes = subscription.episodes.all()
                for episode in episodes:
                    item = SubElement(channel, "item")
                    SubElement(item, "title").text = episode.title
                    SubElement(item, "description").text = episode.description
                    SubElement(item, "pubDate").text = episode.pub_date.strftime(
                        "%a, %d %b %Y %H:%M:%S %z"
                    )
                    SubElement(item, "guid").text = str(episode.uuid)
                    audio_url = episode.audio_url if episode.audio_url else episode.media_link
                    SubElement(item, "enclosure", attrib={"url": audio_url, "type": "audio/mpeg"})
                    SubElement(item, "itunes:duration").text = episode.duration_str
                    pbar.update(1)

        # Write to file
        rss_file_path = os.path.join(settings.MEDIA_ROOT, "feed/combined_feed.xml")
        os.makedirs(os.path.dirname(rss_file_path), exist_ok=True)
        tree = ElementTree(rss)
        tree.write(rss_file_path, encoding="utf-8", xml_declaration=True)

        return rss_file_path

    except Exception as e:
        raise RuntimeError(f"Failed to generate combined RSS feed: {e}")
