# Generated by Django 5.1.4 on 2024-12-25 21:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('rss', '0009_alter_rssfeed_link'),
    ]

    operations = [
        migrations.CreateModel(
            name='RSSMirror',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=500)),
                ('external_feed_link', models.URLField(null=True)),
                ('description', models.TextField(default='')),
                ('pub_date', models.DateTimeField(auto_now_add=True)),
                ('mirrored_content', models.TextField(blank=True)),
                ('last_updated', models.DateTimeField(null=True)),
                ('external_feed', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mirror', to='rss.rssfeed')),
            ],
        ),
    ]
