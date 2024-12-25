from rest_framework import serializers
from rss.models import RSSFeed, Episode

class RSSFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = RSSFeed
        fields = '__all__'
        read_only_fields = ['title','pub_date','description']

class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = '__all__'
        read_only_fields = ['rss_feed','title','link','description','podcast_url','pub_date']