from solo.models import SingletonModel
from subscriptions.models import Episode
from django.db import models


class Player(SingletonModel):
    episode = models.ForeignKey(Episode, null=True, blank=True, on_delete=models.CASCADE)
    current_playtime = models.IntegerField(default=0)
