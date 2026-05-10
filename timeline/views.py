from collections import OrderedDict

from django.shortcuts import render

from timeline.models import Minute


def _format_playback_time(seconds):
    seconds = int(seconds or 0)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def timeline(request):
    minutes = (
        Minute.objects.select_related("episode", "episode__subscription")
        .order_by("-created_at")[:1440]
    )

    days = OrderedDict()
    for minute in minutes:
        day_key = minute.created_at.date()
        days.setdefault(day_key, []).append(
            {
                "pk": minute.pk,
                "time": minute.created_at.strftime("%H:%M"),
                "episode": minute.episode,
                "image_url": minute.image,
                "playback_time_str": _format_playback_time(minute.playback_time),
            }
        )

    grouped = [{"day": day, "minutes": items} for day, items in days.items()]
    context = {"days": grouped, "total_minutes": len(minutes)}
    return render(request, "timeline.html", context=context)
