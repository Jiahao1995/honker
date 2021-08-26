from rest_framework import serializers

from honks.api.serializers import HonkSerializer
from newsfeeds.models import NewsFeed


class NewsFeedSerializer(serializers.ModelSerializer):
    honk = HonkSerializer()

    class Meta:
        model = NewsFeed
        fields = ('id', 'created_at', 'user', 'honk')
