# Generated by Django 5.2 on 2025-05-03 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0003_episode_transcript_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="episode",
            name="low_quality_audio_url",
            field=models.URLField(blank=True, max_length=500),
        ),
    ]
