from rest_framework.test import APIClient

from friendships.models import Friendship
from testing.testcases import TestCase

FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'


class FriendshipApiTests(TestCase):

    def setUp(self):
        super(FriendshipApiTests, self).setUp()

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

    def test_follow(self):
        url = FOLLOW_URL.format(self.jeeves.id)

        # must login first in order to follow others
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # must use POST to follow rather than GET
        response = self.brenda_client.get(url)
        self.assertEqual(response.status_code, 405)

        # one cannot follow oneself
        response = self.jeeves_client.post(url)
        self.assertEqual(response.status_code, 400)

        # follow successfully
        response = self.brenda_client.post(url)
        self.assertEqual(response.status_code, 201)

        # repeat the operation
        response = self.brenda_client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['duplicate'], True)

        # jeeves follows brenda
        count = Friendship.objects.count()
        response = self.jeeves_client.post(FOLLOW_URL.format(self.brenda.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(), count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.jeeves.id)

        # must login first in order to unfollow others
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # must use POST to follow rather than GET
        response = self.brenda_client.get(url)
        self.assertEqual(response.status_code, 405)

        # one cannot follow oneself
        response = self.jeeves_client.post(url)
        self.assertEqual(response.status_code, 400)

        # unfollow successfully
        Friendship.objects.create(from_user=self.brenda, to_user=self.jeeves)
        count = Friendship.objects.count()
        response = self.brenda_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)

        # do nothing before following someone
        count = Friendship.objects.count()
        response = self.brenda_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(Friendship.objects.count(), count)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.brenda.id)

        # POST is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)

        # GET
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followings']), 3)

        # order
        ts0 = response.data['followings'][0]['created_at']
        ts1 = response.data['followings'][1]['created_at']
        ts2 = response.data['followings'][2]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['followings'][0]['user']['username'],
            'brenda_following2',
        )
        self.assertEqual(
            response.data['followings'][1]['user']['username'],
            'brenda_following1',
        )
        self.assertEqual(
            response.data['followings'][2]['user']['username'],
            'brenda_following0',
        )

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.brenda.id)

        # POST is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)

        # GET
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followers']), 2)

        # order
        ts0 = response.data['followers'][0]['created_at']
        ts1 = response.data['followers'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['followers'][0]['user']['username'],
            'brenda_follower1',
        )
        self.assertEqual(
            response.data['followers'][1]['user']['username'],
            'brenda_follower0',
        )
