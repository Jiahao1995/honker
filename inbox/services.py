from django.contrib.contenttypes.models import ContentType
from notifications.signals import notify

from comments.models import Comment
from honks.models import Honk


class NotificationService(object):

    @classmethod
    def send_like_notification(cls, like):
        target = like.content_object
        if like.user == target.user:
            return
        if like.content_type == ContentType.objects.get_for_model(Honk):
            notify.send(
                like.user,
                recipient=target.user,
                verb='liked your honk',
                target=target,
            )
        if like.content_type == ContentType.objects.get_for_model(Comment):
            notify.send(
                like.user,
                recipient=target.user,
                verb='liked your comment',
                target=target,
            )

    @classmethod
    def send_comment_notification(cls, comment):
        if comment.user == comment.honk.user:
            return
        notify.send(
            comment.user,
            recipient=comment.honk.user,
            verb='liked your comment',
            target=comment.honk,
        )
