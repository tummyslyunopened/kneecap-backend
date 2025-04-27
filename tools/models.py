from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class JobQueue(TimeStampedModel):
    description = models.TextField()
    completed = models.BooleanField(default=False)

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["description"],
                condition=models.Q(completed=False),
                name="unique_incomplete_job",
            )
        ]
