from django.contrib.auth.models import User
from django.test import TestCase as DjangoTestCase

from honks.models import Honk


class TestCase(DjangoTestCase):
    def create_user(self, username, email, password=None):
        if password is None:
            password = 'generic password'
        return User.objects.create_user(username, email, password)

    def create_honk(self, user, content=None):
        if content is None:
            content = 'default honk content'
        return Honk.objects.create(user=user, content=content)
