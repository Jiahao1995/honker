from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.api.serializers import UserSerializer
from comments.models import Comment
from honks.models import Honk


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Comment
        fields = ('id', 'honk_id', 'user', 'content', 'created_at')


class CommentSerializerForCreate(serializers.ModelSerializer):
    honk_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = ('content', 'honk_id', 'user_id')

    def validate(self, data):
        honk_id = data['honk_id']
        if not Honk.objects.filter(id=honk_id).exists():
            raise ValidationError({'message': 'honk does not exist'})
        return data

    def create(self, validated_data):
        return Comment.objects.create(
            user_id=validated_data['user_id'],
            honk_id=validated_data['honk_id'],
            content=validated_data['content'],
        )


class CommentSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('content',)

    def update(self, instance, validated_data):
        instance.content = validated_data['content']
        instance.save()
        return instance
