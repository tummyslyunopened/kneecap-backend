# Generated by Django 5.2 on 2025-05-09 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("transcripts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="transcriptsegment",
            name="ai_advertising_reviewed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="transcriptsegment",
            name="ai_detected_advertising",
            field=models.BooleanField(default=False),
        ),
    ]
