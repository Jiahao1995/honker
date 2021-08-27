from django.utils import timezone
from rest_framework.test import APIClient

from comments.models import Comment
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

    def test_destroy(self):
        comment = self.create_comment(self.jeeves, self.honk)
        url = '{}{}/'.format(COMMENT_URL, comment.id)

        # must login first to destroy
        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # cannot destroy if one is not the owner of the honk
        response = self.brenda_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # destroy successfully
        count = Comment.objects.count()
        response = self.jeeves_client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), count - 1)

    def test_update(self):
        comment = self.create_comment(self.jeeves, self.honk, 'original')
        another_honk = self.create_honk(self.brenda)
        url = '{}{}/'.format(COMMENT_URL, comment.id)

        # must login first to update comment using PUT
        response = self.anonymous_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)

        # cannot update if one is not the owner of the honk
        response = self.brenda_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)
        comment.refresh_from_db()
        self.assertNotEqual(comment.content, 'new')

        # can only update the content
        before_updated_at = comment.updated_at
        before_created_at = comment.created_at
        now = timezone.now()
        response = self.jeeves_client.put(url, {
            'content': 'new',
            'user_id': self.brenda.id,
            'honk_id': another_honk.id,
            'created_at': now,
        })
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'new')
        self.assertEqual(comment.user, self.jeeves)
        self.assertEqual(comment.honk, self.honk)
        self.assertEqual(comment.created_at, before_created_at)
        self.assertNotEqual(comment.created_at, now)
        self.assertNotEqual(comment.updated_at, before_updated_at)

    def test_list(self):
        # must have honk_id
        response = self.anonymous_client.get(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        response = self.anonymous_client.get(COMMENT_URL, {
            'honk_id': self.honk.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)

        self.create_comment(self.jeeves, self.honk, '1')
        self.create_comment(self.brenda, self.honk, '2')
        self.create_comment(self.brenda, self.create_honk(self.brenda), '3')
        response = self.anonymous_client.get(COMMENT_URL, {
            'honk_id': self.honk.id,
        })
        self.assertEqual(len(response.data['comments']), 2)
        self.assertEqual(response.data['comments'][0]['content'], '1')
        self.assertEqual(response.data['comments'][1]['content'], '2')

        response = self.anonymous_client.get(COMMENT_URL, {
            'honk_id': self.honk.id,
            'user_id': self.jeeves.id,
        })
        self.assertEqual(len(response.data['comments']), 2)
