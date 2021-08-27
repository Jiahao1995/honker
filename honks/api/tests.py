from rest_framework.test import APIClient

from honks.models import Honk
from testing.testcases import TestCase

HONK_LIST_API = '/api/honks/'
HONK_CREATE_API = '/api/honks/'
HONK_RETRIEVE_API = '/api/honks/{}/'


class HonkApiTests(TestCase):
    def setUp(self):
        self.user1 = self.create_user('user1', 'user1@example.com')
        self.honks1 = [
            self.create_honk(self.user1)
            for i in range(3)
        ]
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2', 'user2@example.com')
        self.honks2 = [
            self.create_honk(self.user2)
            for i in range(2)
        ]

    def test_list(self):
        response = self.anonymous_client.get(HONK_LIST_API)
        self.assertEqual(response.status_code, 400)

        response = self.anonymous_client.get(HONK_LIST_API, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['honks']), 3)
        response = self.anonymous_client.get(HONK_LIST_API, {'user_id': self.user2.id})
        self.assertEqual(len(response.data['honks']), 2)

        self.assertEqual(response.data['honks'][0]['id'], self.honks2[1].id)
        self.assertEqual(response.data['honks'][1]['id'], self.honks2[0].id)

    def test_create(self):
        response = self.anonymous_client.post(HONK_CREATE_API)
        self.assertEqual(response.status_code, 403)

        response = self.user1_client.post(HONK_CREATE_API)
        self.assertEqual(response.status_code, 400)

        response = self.user1_client.post(HONK_CREATE_API, {'content': '1'})
        self.assertEqual(response.status_code, 400)

        response = self.user1_client.post(HONK_CREATE_API, {
            'content': '0' * 141
        })
        self.assertEqual(response.status_code, 400)

        honks_count = Honk.objects.count()
        response = self.user1_client.post(HONK_CREATE_API, {'content': 'Hello World, this is my first honk!'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(Honk.objects.count(), honks_count + 1)

    def test_retrieve(self):
        # must have valid honk id
        url = HONK_RETRIEVE_API.format(-1)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 404)

        honk = self.create_honk(self.user1)
        url = HONK_RETRIEVE_API.format(honk.id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)

        self.create_comment(self.user2, honk, 'Hello World')
        self.create_comment(self.user1, honk, 'Holly Shit')
        response = self.anonymous_client.get(url)
        self.assertEqual(len(response.data['comments']), 2)
