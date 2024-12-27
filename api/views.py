from rest_framework import viewsets
from .pagination import StandardResultsSetPagination
from rss.models import Subscription, Episode
from .serializers import RSSFeedSerializer, EpisodeSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all().order_by("-pub_date")
    serializer_class = RSSFeedSerializer
    pagination_class = StandardResultsSetPagination


class EpisodeViewSet(viewsets.ModelViewSet):
    queryset = Episode.objects.all().order_by("-pub_date")
    serializer_class = EpisodeSerializer
    pagination_class = StandardResultsSetPagination
