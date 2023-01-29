from api.apps.core import models

from django.test import TestCase
from django.contrib.auth import get_user_model


User = get_user_model()


def sample_user(email='test@test.com', password='testpass'):
    return User.objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        email = 'test@dev.com'
        password = 'Password123'

        user = User.objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        email = 'test@DEV.com'

        user = User.objects.create_user(
            email=email,
            password='test123'
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email=None,
                password='test12345'
            )

    def test_create_new_superuser(self):
        user = User.objects.create_superuser(
            email='teste@dev.com',
            password='Test12345'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_resource_str(self):
        resource = models.Resource.objects.create(name='Notebook')

        self.assertEqual(str(resource), resource.name)

    def test_allocate_resource(self):
        resource = models.Resource.objects.create(name='Notebook')

        models.Allocation.objects.create(
            user=sample_user(),
            resource=resource
        )

        self.assertTrue(resource.is_allocated)
