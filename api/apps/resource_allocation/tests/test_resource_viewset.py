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

RESOURCES_URL = reverse('resource_allocation:resource-list')


def detail_url(resource_id):
    return reverse('resource_allocation:resource-detail', args=[resource_id])


class AutenticationTests(APITestCase):
    def test_list_resources_without_autentication(self):
        response = self.client.get(RESOURCES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_resource_without_autentication(self):
        response = self.client.post(RESOURCES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_resource_without_autentication(self):
        url = detail_url(99)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_resource_without_autentication(self):
        url = detail_url(99)
        response = self.client.put(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_resource_without_autentication(self):
        url = detail_url(99)
        response = self.client.patch(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_resource_without_autentication(self):
        url = detail_url(99)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ListResourcesTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            name='Test Báz',
            email='test@test.com',
            password='testpass'
        )

        resources = [
            Resource(
                name='Foo Báz'
            ),
            Resource(
                name='Test Baz'
            ),
            Resource(
                name='Bar',
                is_active=False
            )
        ]

        Resource.objects.bulk_create(resources)

        self.client.force_authenticate(self.user)

    def test_list_resources_with_admin_user(self):
        response = self.client.get(RESOURCES_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_list_resources_with_common_user(self):
        self.user.is_staff = False
        self.user.save()

        response = self.client.get(RESOURCES_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_resources_by_name(self):
        response = self.client.get(
            RESOURCES_URL,
            {'name': 'baz'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_active_resources(self):
        response = self.client.get(
            RESOURCES_URL,
            {'status': 'active'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_inactive_resources(self):
        response = self.client.get(
            RESOURCES_URL,
            {'status': 'inactive'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_allocated_resources(self):
        Allocation.objects.create(
            resource=Resource.objects.first(),
            user=self.user
        )

        response = self.client.get(
            RESOURCES_URL,
            {'status': 'allocated'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_unallocated_resources(self):
        Allocation.objects.create(
            resource=Resource.objects.first(),
            user=self.user
        )

        response = self.client.get(
            RESOURCES_URL,
            {'status': 'unallocated'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class CreateResourceTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            name='test',
            email='test@test.com',
            password='testpass'
        )

        self.client.force_authenticate(self.user)

    def test_create_resource(self):
        payload = {
            'name': 'Notebook',
            'is_active': False
        }

        response = self.client.post(
            RESOURCES_URL,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_resource_with_invalid_name(self):
        payload = {
            'name': ''
        }

        response = self.client.post(
            RESOURCES_URL,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_without_permission(self):
        self.user.is_staff = False
        self.user.save()

        response = self.client.post(RESOURCES_URL)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class GetResourceTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            name='test',
            email='test@test.com',
            password='testpass'
        )

        self.client.force_authenticate(self.user)

    def test_get_resource_success(self):
        resource = Resource.objects.create(
            name='Notebook',
            is_active=False
        )

        url = detail_url(resource.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_resource(self):
        url = detail_url(99)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_inactive_resource_with_common_user(self):
        self.user.is_staff = False
        self.user.save()

        resource = Resource.objects.create(
            name='Notebook',
            is_active=False
        )

        url = detail_url(resource.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UpdateResourceTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            name='test',
            email='test@test.com',
            password='testpass'
        )

        self.resource = Resource.objects.create(
            name='Foo',
            is_active=False
        )

        self.client.force_authenticate(self.user)

    def test_update_resource(self):
        payload = {
            'name': 'Notebook',
            'is_active': True
        }

        url = detail_url(self.resource.id)
        response = self.client.put(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.resource.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.resource.name, payload['name'])
        self.assertTrue(self.resource.is_active)

    def test_update_resource_with_invalid_name(self):
        payload = {
            'name': ''
        }

        url = detail_url(self.resource.id)
        response = self.client.patch(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_resource_without_permission(self):
        self.user.is_staff = False
        self.user.save()

        url = detail_url(99)
        response = self.client.patch(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DeleteResourceTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            name='test',
            email='test@test.com',
            password='testpass'
        )

        self.resource = Resource.objects.create(
            name='Foo',
            is_active=False
        )

        self.client.force_authenticate(self.user)

    def test_delete_resource_success(self):
        url = detail_url(self.resource.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_invalid_resource(self):
        url = detail_url(99)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_resource_with_linked_allocations(self):
        Allocation.objects.create(
            resource=self.resource,
            user=self.user
        )

        url = detail_url(self.resource.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_resource_without_permission(self):
        self.user.is_staff = False
        self.user.save()

        url = detail_url(99)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
