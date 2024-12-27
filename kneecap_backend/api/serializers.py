from django.urls import reverse  # Import reverse
from rest_framework import serializers
from rss.models import Subscription, Episode


class RSSFeedSerializer(serializers.ModelSerializer):
    episodes_count = serializers.IntegerField(read_only=True)
    mirror = serializers.SerializerMethodField()  # Change to SerializerMethodField

    def get_mirror(self, obj):
        request = self.context.get("request")  # Get the request context
        url = reverse("mirror", kwargs={"uuid": obj.mirror.uuid})  # Resolve the URL
        return request.build_absolute_uri(url)  # Construct full absolute URL

    class Meta:
        model = Subscription
        fields = "__all__"
        read_only_fields = [
            "title",
            "pub_date",
            "description",
            "episodes_count",
            "mirror",
        ]


class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = "__all__"
        read_only_fields = [
            "rss_feed",
            "title",
            "description",
            "podcast_url",
            "pub_date",
        ]
