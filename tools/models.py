from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    class Meta:
        abstract = True


class JobQueue(TimeStampedModel, models.Model):
    description = models.TextField()
    completed = models.BooleanField(default=False)
    objects = models.Manager()

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["description"],
                condition=models.Q(completed=False),
                name="unique_incomplete_job",
            )
        ]
