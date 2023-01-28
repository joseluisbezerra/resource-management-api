from api.apps.core.models import (
    Resource,
    Allocation
)

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

import json

User = get_user_model()


def allocations_url(resource_id):
    return reverse('resource_allocation:allocation-list', args=[resource_id])


def detail_url(resource_id, allocation_id):
    return reverse(
        'resource_allocation:allocation-detail',
        args=[
            resource_id,
            allocation_id
        ]
    )


class AutenticationTests(APITestCase):
    def test_list_allocations_without_autentication(self):
        url = allocations_url(99)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_allocation_without_autentication(self):
        url = allocations_url(99)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_allocation_without_autentication(self):
        url = detail_url(99, 99)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_allocation_without_autentication(self):
        url = detail_url(99, 99)
        response = self.client.put(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_allocation_without_autentication(self):
        url = detail_url(99, 99)
        response = self.client.patch(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ListAllocationsTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            name='Test Báz',
            email='test@test.com',
            password='testpass'
        )

        self.resource = Resource.objects.create(
            name='Bar',
            is_active=False
        )

        allocations = [
            Allocation(
                resource=self.resource,
                user=self.user
            ),
            Allocation(
                resource=self.resource,
                return_date=timezone.now(),
                user=self.user
            )
        ]

        Allocation.objects.bulk_create(allocations)

        self.client.force_authenticate(self.user)

    def test_list_allocations_for_resource_with_admin_user(self):
        url = allocations_url(self.resource.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_allocations_for_inactive_resource_with_common_user(self):
        self.user.is_staff = False
        self.user.save()

        url = allocations_url(self.resource.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_allocations_for_invalid_resource(self):
        url = allocations_url(99)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CreateAllocationTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            name='test',
            email='test@test.com',
            password='testpass'
        )

        self.resource = Resource.objects.create(name='Bar')

        self.client.force_authenticate(self.user)

    def test_create_allocation_to_resource(self):
        payload = {
            'allocation_date': "2023-01-28T15:51:49.465311-03:00",
            'return_date': "2023-01-29T15:51:49.465311-03:00"
        }

        url = allocations_url(self.resource.id)
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_allocation_to_resource_with_invalid_allocation_date(self):
        payload = {
            'allocation_date': "",
            'return_date': "2023-01-29T15:51:49.465311-03:00"
        }

        url = allocations_url(self.resource.id)
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_allocation_to_resource_with_invalid_return_date(self):
        payload = {
            'allocation_date': "2023-01-29T15:51:49.465311-03:00",
            'return_date': ""
        }

        url = allocations_url(self.resource.id)
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_allocation_to_inactive_resource_with_admin_user(self):
        self.resource.is_active = False
        self.resource.save()

        payload = {
            'allocation_date': "2023-01-28T15:51:49.465311-03:00",
            'return_date': "2023-01-29T15:51:49.465311-03:00"
        }

        url = allocations_url(self.resource.id)
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_allocation_to_inactive_resource_with_common_user(self):
        self.resource.is_active = False
        self.resource.save()

        self.user.is_staff = False
        self.user.save()

        payload = {
            'allocation_date': "2023-01-28T15:51:49.465311-03:00",
            'return_date': "2023-01-29T15:51:49.465311-03:00"
        }

        url = allocations_url(self.resource.id)
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_allocation_to_invalid_resource(self):
        payload = {
            'allocation_date': "2023-01-28T15:51:49.465311-03:00",
            'return_date': "2023-01-29T15:51:49.465311-03:00"
        }

        url = allocations_url(99)
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GetAllocationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            name='test',
            email='test@test.com',
            password='testpass'
        )

        self.resource = Resource.objects.create(
            name='Bar',
            is_active=False
        )

        self.client.force_authenticate(self.user)

    def test_get_allocation_success(self):
        allocation = Allocation.objects.create(
            resource=self.resource,
            user=self.user
        )

        url = detail_url(self.resource.id, allocation.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_allocation(self):
        url = detail_url(self.resource.id, 99)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_allocation_for_inactive_resource_with_common_user(self):
        self.user.is_staff = False
        self.user.save()

        allocation = Allocation.objects.create(
            user=self.user,
            resource=self.resource
        )

        url = detail_url(self.resource.id, allocation.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UpdateAllocationTests(APITestCase):

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

        self.allocation = Allocation.objects.create(
            resource=self.resource,
            user=self.user
        )

        self.client.force_authenticate(self.user)

    def test_update_allocation(self):
        payload = {
            'allocation_date': "2023-01-28T15:51:49.465311-03:00",
            'return_date': "2023-01-29T15:51:49.465311-03:00"
        }

        url = detail_url(self.resource.id, self.allocation.id)
        response = self.client.put(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_allocation_with_invalid_allocation_date(self):
        payload = {
            'allocation_date': '',
            'return_date': "2023-01-29T15:51:49.465311-03:00"
        }

        url = detail_url(self.resource.id, self.allocation.id)
        response = self.client.patch(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_allocation_with_invalid_return_date(self):
        payload = {
            'allocation_date': '2023-01-29T15:51:49.465311-03:00',
            'return_date': ''
        }

        url = detail_url(self.resource.id, self.allocation.id)
        response = self.client.patch(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_invalid_allocation(self):
        url = detail_url(self.resource.id, 99)
        response = self.client.patch(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_allocation_to_inactive_resource_with_common_user(self):
        self.user.is_staff = False
        self.user.save()

        url = detail_url(self.resource.id, self.allocation.id)
        response = self.client.patch(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
