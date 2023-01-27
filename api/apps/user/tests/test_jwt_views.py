from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

import json


TOKEN_OBTAIN_PAIR_URL = reverse('user:token_obtain_pair')
TOKEN_REFRESH_URL = reverse('user:token_refresh')

User = get_user_model()


def create_user(**params):
    """Helper function to create new user"""
    return User.objects.create_user(**params)


class JWTTests(APITestCase):

    def test_create_token_for_user(self):
        payload = {
            'email': 'test@test.com',
            'password': 'testpass'
        }

        create_user(**payload)

        response = self.client.post(
            TOKEN_OBTAIN_PAIR_URL,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refresh_token_for_user(self):
        payload = {
            'email': 'test@test.com',
            'password': 'testpass'
        }

        create_user(**payload)

        token_pair_response = self.client.post(
            TOKEN_OBTAIN_PAIR_URL,
            data=json.dumps(payload),
            content_type='application/json'
        )

        new_payload = {
            'refresh': token_pair_response.data['refresh']
        }

        response = self.client.post(
            TOKEN_REFRESH_URL,
            data=json.dumps(new_payload),
            content_type='application/json'
        )

        self.assertIn('access', response.data)
        self.assertNotIn('refresh', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_with_invalid_credentials(self):
        create_user(email='test@test.com', password='testpass')

        payload = {
            'email': 'test@test.com',
            'password': 'wrong'
        }

        response = self.client.post(
            TOKEN_OBTAIN_PAIR_URL,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_token_to_inactive_user(self):
        create_user(
            email='test@test.com',
            password='testpass',
            is_active=False
        )

        payload = {
            'email': 'test@test.com',
            'password': 'testpass'
        }

        response = self.client.post(
            TOKEN_OBTAIN_PAIR_URL,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_with_invalid_credentials(self):
        payload = {
            'refresh': 'test'
        }

        response = self.client.post(
            TOKEN_REFRESH_URL,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertNotIn('access', response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_token_no_user(self):
        payload = {
            'email': 'test@test.com',
            'password': 'testpass'
        }

        response = self.client.post(
            TOKEN_OBTAIN_PAIR_URL,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_token_missing_field(self):
        payload = {
            'email': 'one',
            'password': ''
        }

        response = self.client.post(
            TOKEN_OBTAIN_PAIR_URL,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_token_missing_field(self):
        payload = {
            'refresh': ''
        }

        response = self.client.post(
            TOKEN_REFRESH_URL,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertNotIn('access', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
