# Generated by Django 5.1.4 on 2024-12-27 02:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rss', '0003_remove_episode_local_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='episode',
            name='local_path',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]
