from django.urls import path
from .views import episode_list  # Import the episode_list view

urlpatterns = [
    path('episodes/', episode_list, name='episode_list'),  # Add URL pattern for episode list
    # ... other URL patterns ...
] 