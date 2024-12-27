from rest_framework import viewsets
from .pagination import StandardResultsSetPagination
from rss.models import RSSFeed, Episode
from .serializers import RSSFeedSerializer, EpisodeSerializer

class RSSFeedViewSet(viewsets.ModelViewSet):
    queryset = RSSFeed.objects.all().order_by('-pub_date')
    serializer_class = RSSFeedSerializer
    pagination_class = StandardResultsSetPagination

class EpisodeViewSet(viewsets.ModelViewSet):
    queryset = Episode.objects.all().order_by('-pub_date')
    serializer_class = EpisodeSerializer
    pagination_class = StandardResultsSetPagination