# Generated by Django 5.1.4 on 2024-12-27 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rss', '0004_episode_local_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='rssfeed',
            name='image',
            field=models.URLField(blank=True, null=True),
        ),
    ]
