from django.urls import path
from .views import add_rss_feed, stripped_mirror_view

urlpatterns = [
    path('add/', add_rss_feed, name='add_rss_feed'),
    path('stripped/<int:id>/', stripped_mirror_view, name='stripped_mirror'),
    # ... other URL patterns ...
]