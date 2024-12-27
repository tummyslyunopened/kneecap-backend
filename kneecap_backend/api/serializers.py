from rest_framework import serializers
from rss.models import RSSFeed, Episode

class RSSFeedSerializer(serializers.ModelSerializer):
    episodes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = RSSFeed
        fields = '__all__'
        read_only_fields = ['title', 'pub_date', 'description', 'episodes_count']

class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = '__all__'
        read_only_fields = ['rss_feed', 'title', 'description', 'podcast_url', 'pub_date']