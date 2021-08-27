from testing.testcases import TestCase

LIKE_BASE_URL = '/api/likes/'


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
