from django.urls import reverse
from rest_framework import serializers
from rss.models import Subscription, Episode


class RSSFeedSerializer(serializers.ModelSerializer):
    episodes_count = serializers.IntegerField(read_only=True)
    mirror = serializers.SerializerMethodField()

    def get_mirror(self, obj):
        request = self.context.get("request")
        url = reverse("mirror", kwargs={"uuid": obj.mirror.uuid})
        return request.build_absolute_uri(url)

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
