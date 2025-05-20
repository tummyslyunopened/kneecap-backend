from django.db import models


class GlobalThrottle(models.Model):
    key = models.CharField(max_length=100, unique=True)
    last_called = models.DateTimeField(null=True, blank=True)
    interval_seconds = models.IntegerField()
    objects = models.Manager()

    def __str__(self):
        return f"{self.key} - {self.last_called} - {self.interval_seconds}"
