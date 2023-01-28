from api.apps.core.models import (
    Resource,
    Allocation
)

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

import json

User = get_user_model()

USERS_URL = reverse('user:user-list')


def detail_url(user_id):
    return reverse('user:user-detail', args=[user_id])


class AutenticationTests(APITestCase):
    def test_list_users_without_autentication(self):
        response = self.client.get(USERS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_user_without_autentication(self):
        response = self.client.post(USERS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_user_without_autentication(self):
        url = detail_url(99)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_without_autentication(self):
        url = detail_url(99)
        response = self.client.put(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_user_without_autentication(self):
        url = detail_url(99)
        response = self.client.patch(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_user_without_autentication(self):
        url = detail_url(99)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ListUsersTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            name='Test Báz',
            email='test@test.com',
            password='testpass'
        )

        User.objects.create(
            name='Foo Báz',
            email='foo@foo.com',
            password='testpass',
            is_active=False
        )

        User.objects.create(
            name='Bar',
            email='bar@bar.com',
            password='testpass'
        )

        self.client.force_authenticate(self.user)

    def test_list_users(self):
        response = self.client.get(USERS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_filter_users_by_name(self):
        response = self.client.get(
            USERS_URL,
            {'name': 'baz'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_admin_users(self):
        response = self.client.get(
            USERS_URL,
            {'type': 'admin'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_active_users(self):
        response = self.client.get(
            USERS_URL,
            {'type': 'active'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_inactive_users(self):
        response = self.client.get(
            USERS_URL,
            {'type': 'inactive'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_users_without_permission(self):
        self.user.is_staff = False
        self.user.save()

        response = self.client.get(USERS_URL)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CreateUserTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            name='test',
            email='test@test.com',
            password='testpass'
        )

        self.client.force_authenticate(self.user)

    def test_create_user(self):
        payload = {
            'name': 'cool name',
            'password': 'newpassword123456',
            'email': 'foo@bar.com',
            'is_staff': True
        }

        response = self.client.post(
            USERS_URL,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_with_existing_email(self):
        User.objects.create(
            name='foo bar',
            email='foo@bar.com',
            password='foobar7'
        )

        payload = {
            'name': 'cool name',
            'password': 'newpassword123456',
            'email': 'foo@bar.com'
        }

        response = self.client.post(
            USERS_URL,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_invalid_email(self):
        payload = {
            'name': 'cool name',
            'password': 'newpassword123456',
            'email': 'invalidemail'
        }

        response = self.client.post(
            USERS_URL,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_invalid_name(self):
        payload = {
            'name': '',
            'password': 'newpassword123456',
            'email': 'foo@bar.com'
        }

        response = self.client.post(
            USERS_URL,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_weak_password_password(self):
        payload = {
            'name': 'cool name',
            'email': 'foo@bar.com',
            'password': '123'
        }

        response = self.client.post(
            USERS_URL,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_without_permission(self):
        self.user.is_staff = False
        self.user.save()

        response = self.client.post(USERS_URL)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class GetUserTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            name='test',
            email='test@test.com',
            password='testpass'
        )

        self.client.force_authenticate(self.user)

    def test_get_user_success(self):
        user = User.objects.create(
            name='foo bar',
            email='foo@bar.com',
            password='foobar7'
        )

        url = detail_url(user.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_user(self):
        url = detail_url(99)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user_without_permission(self):
        self.user.is_staff = False
        self.user.save()

        url = detail_url(99)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UpdateUserTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            name='test',
            email='test@test.com',
            password='testpass'
        )

        self.client.force_authenticate(self.user)

    def test_update_user(self):
        payload = {
            'name': 'cool name',
            'password': 'newpassword123456',
            'email': 'foo@bar.com',
            'is_staff': True
        }

        url = detail_url(self.user.id)
        response = self.client.put(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(self.user.name, payload['name'])
        self.assertEqual(self.user.email, payload['email'])

    def test_update_user_with_existing_email(self):
        User.objects.create(
            name='foo bar',
            email='foo@bar.com',
            password='foobar7'
        )

        payload = {
            'email': 'foo@bar.com'
        }

        url = detail_url(self.user.id)
        response = self.client.patch(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_with_invalid_email(self):
        payload = {
            'email': 'invalidemail'
        }

        url = detail_url(self.user.id)
        response = self.client.patch(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_with_invalid_name(self):
        payload = {
            'name': ''
        }

        url = detail_url(self.user.id)
        response = self.client.patch(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_with_weak_password_password(self):
        payload = {
            'password': '123'
        }

        url = detail_url(self.user.id)
        response = self.client.patch(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_without_permission(self):
        self.user.is_staff = False
        self.user.save()

        url = detail_url(99)
        response = self.client.patch(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DeleteUserTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            name='test',
            email='test@test.com',
            password='testpass'
        )

        self.client.force_authenticate(self.user)

    def test_delete_user_success(self):
        user = User.objects.create(
            name='foo bar',
            email='foo@bar.com',
            password='foobar7'
        )

        url = detail_url(user.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_invalid_user(self):
        url = detail_url(99)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_user_with_linked_allocations(self):
        user = User.objects.create(
            name='foo bar',
            email='foo@bar.com',
            password='foobar7'
        )

        resource = Resource.objects.create(name='')

        Allocation.objects.create(
            resource=resource,
            user=user
        )

        url = detail_url(user.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_user_without_permission(self):
        self.user.is_staff = False
        self.user.save()

        url = detail_url(99)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
