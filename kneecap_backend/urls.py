from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('feed/', include('kneecap_backend.feed.urls')),  # Include the feed app URLs
] 