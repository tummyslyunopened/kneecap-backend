from django.urls import path
from .views import subscriptions, mirror

urlpatterns = [
    path("subscriptions/", subscriptions, name="subscriptions"),
    path("mirror/<str:uuid>/", mirror, name="mirror"),
]
