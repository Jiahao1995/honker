from rest_framework.test import APIClient

from honks.models import Honk
from testing.testcases import TestCase

HONK_LIST_API = '/api/honks/'
HONK_CREATE_API = '/api/honks/'


class HonkApiTests(TestCase):
    def setUp(self):
        self.anonymous_client = APIClient()
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

    def test_list_api(self):
        response = self.anonymous_client.get(HONK_LIST_API)
        self.assertEqual(response.status_code, 400)

        response = self.anonymous_client.get(HONK_LIST_API, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['honks']), 3)
        response = self.anonymous_client.get(HONK_LIST_API, {'user_id': self.user2.id})
        self.assertEqual(len(response.data['honks']), 2)

        self.assertEqual(response.data['honks'][0]['id'], self.honks2[1].id)
        self.assertEqual(response.data['honks'][1]['id'], self.honks2[0].id)

    def test_create_api(self):
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
