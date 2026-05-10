from django.urls import path

from timeline.views import timeline

urlpatterns = [
    path("", timeline, name="timeline"),
]
