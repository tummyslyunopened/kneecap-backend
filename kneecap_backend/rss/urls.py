from django.urls import path
from .views import add_rss_feed

urlpatterns = [
    path('add/', add_rss_feed, name='add_rss_feed'),
    # ... other URL patterns ...
]