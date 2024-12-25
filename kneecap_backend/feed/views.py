from django.shortcuts import render
from rss.models import Episode  # Import the Episode model

# Create your views here.

def episode_list(request):
    episodes = Episode.objects.all().order_by('pub_date')  # Fetch all episodes in chronological order
    return render(request, 'episode_list.html', {'episodes': episodes})  # Render the template with episodes

