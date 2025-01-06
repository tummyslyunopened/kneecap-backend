# Generated by Django 5.1.4 on 2025-01-05 09:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0002_alter_subscription_recent_episode_pub_date"),
    ]

    operations = [
        migrations.CreateModel(
            name="Event",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name="episode",
            name="hidden",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="EpisodeWatchEvent",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="subscriptions.event",
                    ),
                ),
                (
                    "episode",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="watch_events",
                        to="subscriptions.episode",
                    ),
                ),
            ],
            bases=("subscriptions.event",),
        ),
    ]
