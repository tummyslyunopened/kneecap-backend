from django.urls import path, include
from rss import urls as rss_urls
from api import urls as api_urls
from opml import urls as opml_urls
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
   path('rss/', include(rss_urls)),
   path('api/', include(api_urls)),
   path('api/opml/', include(opml_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
