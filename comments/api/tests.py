from rest_framework.test import APIClient

from testing.testcases import TestCase

COMMENT_URL = '/api/comments/'


class CommentApiTests(TestCase):

    def setUp(self):
        self.jeeves = self.create_user('jeeves')
        self.jeeves_client = APIClient()
        self.jeeves_client.force_authenticate(self.jeeves)

        self.brenda = self.create_user('brenda')
        self.brenda_client = APIClient()
        self.brenda_client.force_authenticate(self.brenda)

        self.honk = self.create_honk(self.jeeves)

    def test_create(self):
        # must login first to comment
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)

        # must comment with parameters
        response = self.jeeves_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # must comment with some content
        response = self.jeeves_client.post(COMMENT_URL, {'honk_id': self.honk.id})
        self.assertEqual(response.status_code, 400)

        # must comment on a honk
        response = self.jeeves_client.post(COMMENT_URL, {'content': '1'})
        self.assertEqual(response.status_code, 400)

        # content cannot be too long
        response = self.jeeves_client.post(COMMENT_URL, {
            'honk_id': self.honk.id,
            'content': '1' * 141,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'], True)

        # comment successfully
        response = self.jeeves_client.post(COMMENT_URL, {
            'honk_id': self.honk.id,
            'content': '1',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.jeeves.id)
        self.assertEqual(response.data['honk_id'], self.honk.id)
        self.assertEqual(response.data['content'], '1')
