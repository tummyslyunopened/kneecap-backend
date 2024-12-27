from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubscriptionViewSet, EpisodeViewSet

router = DefaultRouter()
router.register(r"subscriptions", SubscriptionViewSet)
router.register(r"episodes", EpisodeViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
