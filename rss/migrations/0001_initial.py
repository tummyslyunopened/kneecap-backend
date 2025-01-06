# Generated by Django 5.1.4 on 2025-01-05 08:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("subscriptions", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="RSSSubscription",
            fields=[
                (
                    "subscription_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="subscriptions.subscription",
                    ),
                ),
            ],
            bases=("subscriptions.subscription",),
        ),
        migrations.CreateModel(
            name="RSSEpisodeDownloadQueue",
            fields=[
                (
                    "queue_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="subscriptions.queue",
                    ),
                ),
                (
                    "episode",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="download_queue",
                        to="subscriptions.episode",
                    ),
                ),
            ],
            bases=("subscriptions.queue",),
        ),
        migrations.CreateModel(
            name="RSSSubscriptionRefreshQueue",
            fields=[
                (
                    "queue_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="subscriptions.queue",
                    ),
                ),
                (
                    "subscription",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="refreshes",
                        to="rss.rsssubscription",
                    ),
                ),
            ],
            bases=("subscriptions.queue",),
        ),
    ]
