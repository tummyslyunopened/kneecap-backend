# Generated by Django 5.2 on 2025-06-02 08:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("subscriptions", "0008_remove_feed_has_local_audio_feed_has_audio"),
    ]

    operations = [
        migrations.CreateModel(
            name="Minute",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(unique=True)),
                ("playback_time", models.DurationField()),
                (
                    "episode",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="minutes",
                        to="subscriptions.episode",
                    ),
                ),
            ],
        ),
    ]
