# Generated by Django 5.1.4 on 2024-12-25 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rss', '0008_remove_episode_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rssfeed',
            name='link',
            field=models.URLField(),
        ),
    ]
