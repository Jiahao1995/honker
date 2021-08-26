from django.contrib.auth.models import User
from django.db import models

from honks.models import Honk


class NewsFeed(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    honk = models.ForeignKey(Honk, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        unique_together = (('user', 'honk'),)
        ordering = ('user', '-created_at',)

    def __str__(self):
        return f'{self.created_at} inbox of {self.user}: {self.honk}'
