from django.urls import path
from .views import OPMLImportView

urlpatterns = [
    path("import/", OPMLImportView.as_view(), name="opml-import"),
]
