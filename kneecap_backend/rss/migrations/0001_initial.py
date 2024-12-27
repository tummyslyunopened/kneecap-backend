import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Feed",
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
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("title", models.CharField(default="", max_length=500)),
                ("description", models.TextField(default="")),
                ("pub_date", models.DateTimeField(auto_now_add=True)),
                ("image", models.URLField(blank=True, null=True)),
                ("mirror", models.TextField(null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Subscription",
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
                ("link", models.URLField()),
                ("title", models.CharField(default="", max_length=500)),
                ("description", models.TextField(default="")),
                ("pub_date", models.DateTimeField(auto_now_add=True)),
                ("image", models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Episode",
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
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField()),
                ("pub_date", models.DateTimeField()),
                ("media", models.URLField(blank=True, null=True)),
                ("played", models.BooleanField(default=False)),
                ("current_playback_time", models.DurationField(blank=True, null=True)),
                ("url", models.URLField(blank=True, max_length=500, null=True)),
                (
                    "feed",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="episodes",
                        to="rss.feed",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="feed",
            name="subscription",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="mirror",
                to="rss.subscription",
            ),
        ),
    ]
