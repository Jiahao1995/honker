from notifications.models import Notification

from inbox.services import NotificationService
from testing.testcases import TestCase


class NotificationServiceTests(TestCase):

    def setUp(self):
        self.jeeves = self.create_user('jeeves')
        self.brenda = self.create_user('brenda')
        self.jeeves_honk = self.create_honk(self.jeeves)

    def test_send_comment_notification(self):
        # do not dispatch notification if honk user == comment user
        comment = self.create_comment(self.jeeves, self.jeeves_honk)
        NotificationService.send_comment_notification(comment)
        self.assertEqual(Notification.objects.count(), 0)

        # dispatch notification if honk user != comment user
        comment = self.create_comment(self.brenda, self.jeeves_honk)
        NotificationService.send_comment_notification(comment)
        self.assertEqual(Notification.objects.count(), 1)

    def test_send_like_notification(self):
        # do not dispatch notification if honk user == like user
        like = self.create_like(self.jeeves, self.jeeves_honk)
        NotificationService.send_like_notification(like)
        self.assertEqual(Notification.objects.count(), 0)

        # dispatch notification if honk user != like user
        like = self.create_like(self.brenda, self.jeeves_honk)
        NotificationService.send_like_notification(like)
        self.assertEqual(Notification.objects.count(), 1)
