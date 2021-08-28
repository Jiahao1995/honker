from rest_framework.test import APIClient

from testing.testcases import TestCase

LIKE_BASE_URL = '/api/likes/'
LIKE_CANCEL_URL = '/api/likes/cancel/'
COMMENT_LIST_API = '/api/comments/'
HONK_LIST_API = '/api/honks/'
HONK_DETAIL_API = '/api/honks/{}/'
NEWSFEED_LIST_API = '/api/newsfeeds/'


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

    def test_likes_in_comments_api(self):
        honk = self.create_honk(self.jeeves)
        comment = self.create_comment(self.jeeves, honk)

        # must login first to cancel like
        anonymous_client = APIClient()
        response = anonymous_client.get(COMMENT_LIST_API, {'honk_id': honk.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], False)
        self.assertEqual(response.data['comments'][0]['likes_count'], 0)

        # test comments list api
        response = self.brenda_client.get(COMMENT_LIST_API, {'honk_id': honk.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], False)
        self.assertEqual(response.data['comments'][0]['likes_count'], 0)
        self.create_like(self.brenda, comment)
        response = self.brenda_client.get(COMMENT_LIST_API, {'honk_id': honk.id})
        self.assertEqual(response.data['comments'][0]['has_liked'], True)
        self.assertEqual(response.data['comments'][0]['likes_count'], 1)

        # test honk detail api
        self.create_like(self.jeeves, comment)
        url = HONK_DETAIL_API.format(honk.id)
        response = self.brenda_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], True)
        self.assertEqual(response.data['comments'][0]['likes_count'], 2)

    def test_likes_in_tweets_api(self):
        honk = self.create_honk(self.jeeves)

        # test tweet detail api
        url = HONK_DETAIL_API.format(honk.id)
        response = self.brenda_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_liked'], False)
        self.assertEqual(response.data['likes_count'], 0)
        self.create_like(self.brenda, honk)
        response = self.brenda_client.get(url)
        self.assertEqual(response.data['has_liked'], True)
        self.assertEqual(response.data['likes_count'], 1)

        # test tweets list api
        response = self.brenda_client.get(HONK_LIST_API, {'user_id': self.jeeves.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['honks'][0]['has_liked'], True)
        self.assertEqual(response.data['honks'][0]['likes_count'], 1)

        # test newsfeeds list api
        self.create_like(self.jeeves, honk)
        self.create_newsfeed(self.brenda, honk)
        response = self.brenda_client.get(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['newsfeeds'][0]['honk']['has_liked'], True)
        self.assertEqual(response.data['newsfeeds'][0]['honk']['likes_count'], 2)

        # test likes details
        url = HONK_DETAIL_API.format(honk.id)
        response = self.brenda_client.get(url)
        self.assertEqual(len(response.data['likes']), 2)
        self.assertEqual(response.data['likes'][0]['user']['id'], self.jeeves.id)
        self.assertEqual(response.data['likes'][1]['user']['id'], self.brenda.id)
