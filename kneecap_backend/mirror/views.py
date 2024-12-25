from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import RSSMirror

# Create your views here.

def serve_mirror(request, mirror_id):
    mirror = get_object_or_404(RSSMirror, id=mirror_id)
    content = mirror.get_mirror_content()
    return HttpResponse(content, content_type='application/xml')
