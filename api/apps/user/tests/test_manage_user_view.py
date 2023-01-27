from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

import json


ME_URL = reverse('user:me')

User = get_user_model()


class AutenticationTests(APITestCase):

    def test_retrieve_profile_without_autentication(self):
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_without_autentication(self):
        response = self.client.put(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_profile_without_autentication(self):
        response = self.client.patch(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GetProfileTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            email='test@test.com',
            password='testpass'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_profile_success(self):
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                'name': self.user.name,
                'email': self.user.email
            }
        )


class UpdateProfileTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            name='test',
            email='test@test.com',
            password='testpass'
        )

        self.client.force_authenticate(self.user)

    def test_update_profile_success(self):
        payload = {
            'name': 'cool name',
            'password': 'newpassword123456',
            'email': 'foo@bar.com'
        }

        response = self.client.put(
            ME_URL,
            data=payload,
            format='multipart'
        )

        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(self.user.name, payload['name'])
        self.assertEqual(self.user.email, payload['email'])

    def test_update_profile_with_existing_email(self):
        User.objects.create(
            name='foo bar',
            email='foo@bar.com',
            password='foobar7'
        )

        payload = {
            'email': 'foo@bar.com'
        }

        response = self.client.patch(
            ME_URL,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_profile_with_invalid_email(self):
        payload = {
            'email': 'invalidemail'
        }

        response = self.client.patch(
            ME_URL,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_profile_with_invalid_name(self):
        payload = {
            'name': ''
        }

        response = self.client.patch(
            ME_URL,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_profile_with_weak_password_password(self):
        payload = {
            'password': '123'
        }

        response = self.client.patch(
            ME_URL,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
