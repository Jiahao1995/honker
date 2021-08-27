from rest_framework.test import APIClient

from friendships.models import Friendship
from testing.testcases import TestCase

NEWSFEEDS_URL = '/api/newsfeeds/'
POST_HONKS_URL = '/api/honks/'
FOLLOW_URL = '/api/friendships/{}/follow/'


class NewsFeedApiTests(TestCase):

    def setUp(self):
        super(NewsFeedApiTests, self).setUp()

        self.jeeves = self.create_user('jeeves')
        self.jeeves_client = APIClient()
        self.jeeves_client.force_authenticate(self.jeeves)

        self.brenda = self.create_user('brenda')
        self.brenda_client = APIClient()
        self.brenda_client.force_authenticate(self.brenda)

        for i in range(2):
            follower = self.create_user('brenda_follower{}'.format(i))
            Friendship.objects.create(from_user_id=follower.id, to_user_id=self.brenda.id)

        for i in range(3):
            following = self.create_user('brenda_following{}'.format(i))
            Friendship.objects.create(from_user_id=self.brenda.id, to_user_id=following.id)

    def test_list(self):
        # must login in order to receive newsfeeds
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 403)

        # must use GET rather than POST
        response = self.jeeves_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 405)

        # nothing for a new client
        response = self.jeeves_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['newsfeeds']), 0)

        # one can see his own honks
        self.jeeves_client.post(POST_HONKS_URL, {'content': 'Hello World'})
        response = self.jeeves_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 1)

        # one can see his friends' honks
        self.jeeves_client.post(FOLLOW_URL.format(self.brenda.id))
        response = self.brenda_client.post(POST_HONKS_URL, {'content': 'Hello Honker', })
        posted_honk_id = response.data['id']
        response = self.jeeves_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 2)
        self.assertEqual(response.data['newsfeeds'][0]['honk']['id'], posted_honk_id)
