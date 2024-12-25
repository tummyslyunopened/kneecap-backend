from rest_framework import viewsets
from rss.models import RSSFeed, Episode
from .serializers import RSSFeedSerializer, EpisodeSerializer

class RSSFeedViewSet(viewsets.ModelViewSet):
    queryset = RSSFeed.objects.all()
    serializer_class = RSSFeedSerializer

class EpisodeViewSet(viewsets.ModelViewSet):
    queryset = Episode.objects.all()
    serializer_class = EpisodeSerializer