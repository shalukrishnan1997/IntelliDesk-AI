import uuid

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase


User = get_user_model()


class UserModelTests(TestCase):
    def test_user_uses_uuid_as_primary_key(self):
        user = User.objects.create_user(
            username="customer_one",
            email="customer1@example.com",
            password="StrongPass123!",
        )

        self.assertIsInstance(user.id, uuid.UUID)

    def test_new_user_has_customer_role_by_default(self):
        user = User.objects.create_user(
            username="customer_two",
            email="customer2@example.com",
            password="StrongPass123!",
        )

        self.assertEqual(user.role, User.Role.CUSTOMER)

    def test_user_email_must_be_unique(self):
        User.objects.create_user(
            username="customer_three",
            email="duplicate@example.com",
            password="StrongPass123!",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(
                    username="customer_four",
                    email="duplicate@example.com",
                    password="StrongPass123!",
                )

    def test_user_string_representation_is_username(self):
        user = User.objects.create_user(
            username="customer_five",
            email="customer5@example.com",
            password="StrongPass123!",
        )

        self.assertEqual(str(user), "customer_five")