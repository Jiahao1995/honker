from datetime import timedelta

from testing.testcases import TestCase

from utils.time_helpers import utc_now


class HonkTests(TestCase):
    def setUp(self):
        self.jeeves = self.create_user('jeeves')
        self.honk = self.create_honk(self.jeeves, content='Hello World')

    def test_hours_to_now(self):
        self.honk.created_at = utc_now() - timedelta(hours=10)
        self.honk.save()
        self.assertEqual(self.honk.hours_to_now, 10)

    def test_like_set(self):
        self.create_like(self.jeeves, self.honk)
        self.assertEqual(self.honk.like_set.count(), 1)

        self.create_like(self.jeeves, self.honk)
        self.assertEqual(self.honk.like_set.count(), 1)

        brenda = self.create_user('brenda')
        self.create_like(brenda, self.honk)
        self.assertEqual(self.honk.like_set.count(), 2)
