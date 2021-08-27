from testing.testcases import TestCase

LIKE_BASE_URL = '/api/likes/'
LIKE_CANCEL_URL = '/api/likes/cancel/'


class LikeApiTests(TestCase):

    def setUp(self):
        self.jeeves, self.jeeves_client = self.create_user_and_client('jeeves')
        self.brenda, self.brenda_client = self.create_user_and_client('brenda')

    def test_honk_likes(self):
        honk = self.create_honk(self.jeeves)
        data = {'content_type': 'honk', 'object_id': honk.id}

        # must login first to like
        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 403)

        # GET is not allowed
        response = self.jeeves_client.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 405)

        # like successfully
        response = self.jeeves_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(honk.like_set.count(), 1)

        # duplicated likes
        self.jeeves_client.post(LIKE_BASE_URL, data)
        self.assertEqual(honk.like_set.count(), 1)
        self.brenda_client.post(LIKE_BASE_URL, data)
        self.assertEqual(honk.like_set.count(), 2)

    def test_comment_likes(self):
        honk = self.create_honk(self.jeeves)
        comment = self.create_comment(self.brenda, honk)
        data = {'content_type': 'comment', 'object_id': comment.id}

        # must login first to like
        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 403)

        # GET is not allowed
        response = self.jeeves_client.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 405)

        # wrong content type
        response = self.jeeves_client.post(LIKE_BASE_URL, {
            'content_type': 'wrong content type',
            'object_id': comment.id,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content_type' in response.data['errors'], True)

        # wrong object_id
        response = self.jeeves_client.post(LIKE_BASE_URL, {
            'content_type': 'comment',
            'object_id': -1,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('object_id' in response.data['errors'], True)

        # like successfully
        response = self.jeeves_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(comment.like_set.count(), 1)

        # duplicated likes
        response = self.jeeves_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(comment.like_set.count(), 1)
        self.brenda_client.post(LIKE_BASE_URL, data)
        self.assertEqual(comment.like_set.count(), 2)

    def test_cancel(self):
        honk = self.create_honk(self.jeeves)
        comment = self.create_comment(self.brenda, honk)
        like_comment_data = {'content_type': 'comment', 'object_id': comment.id}
        like_honk_data = {'content_type': 'honk', 'object_id': honk.id}
        self.jeeves_client.post(LIKE_BASE_URL, like_comment_data)
        self.brenda_client.post(LIKE_BASE_URL, like_honk_data)
        self.assertEqual(honk.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 1)

        # must login first to cancel
        response = self.anonymous_client.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 403)

        # GET is not allowed
        response = self.jeeves_client.get(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 405)

        # wrong content type
        response = self.jeeves_client.post(LIKE_CANCEL_URL, {
            'content_type': 'wrong',
            'object_id': 1,
        })
        self.assertEqual(response.status_code, 400)

        # wrong object id
        response = self.jeeves_client.post(LIKE_CANCEL_URL, {
            'content_type': 'comment',
            'object_id': -1,
        })
        self.assertEqual(response.status_code, 400)

        # brenda has not liked comment before
        response = self.brenda_client.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(honk.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 1)

        # cancel jeeves's comment like successfully
        response = self.jeeves_client.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(honk.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 0)

        # jeeves has not liked honk before
        response = self.jeeves_client.post(LIKE_CANCEL_URL, like_honk_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(honk.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 0)

        # cancel brenda's honk like successfully
        response = self.brenda_client.post(LIKE_CANCEL_URL, like_honk_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(honk.like_set.count(), 0)
        self.assertEqual(comment.like_set.count(), 0)
