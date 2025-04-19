from django.db import models


class Queue(models.Model):
    description = models.TextField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["description"],
                condition=models.Q(completed=False),
                name="unique_incomplete_job",
            )
        ]