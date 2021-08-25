from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from honks.models import Honk
from utils.time_helpers import utc_now


class HonkTests(TestCase):
    def test_hours_to_now(self):
        user = User.objects.create_user(username='admin')
        honk = Honk.objects.create(user=user, content='Hello World')
        honk.created_at = utc_now() - timedelta(hours=10)
        honk.save()
        self.assertEqual(honk.hours_to_now, 10)
