from django.contrib.auth.models import User
from django.db import models

from honks.models import Honk


class Comment(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    honk = models.ForeignKey(Honk, null=True, on_delete=models.SET_NULL)
    content = models.TextField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        index_together = (('honk', 'created_at'),)

    def __str__(self):
        return '{} - {} says {} at honk {}'.format(
            self.created_at,
            self.user,
            self.content,
            self.honk_id,
        )
