from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from rest_framework.test import APIRequestFactory, APITestCase

from accounts.permissions import (
    IsAdminOrManagerRole,
    IsAdminRole,
)


User = get_user_model()


class IsAdminRoleTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = IsAdminRole()

    def test_admin_user_has_permission(self):
        user = User.objects.create_user(
            username="admin_user",
            email="admin@example.com",
            password="StrongPassword@123",
            role="admin",
        )

        request = self.factory.get("/test/")
        request.user = user

        has_permission = self.permission.has_permission(
            request,
            view=None,
        )

        self.assertTrue(has_permission)

    def test_non_admin_users_do_not_have_permission(self):
        for role in ["manager", "agent", "customer"]:
            with self.subTest(role=role):
                user = User.objects.create_user(
                    username=f"{role}_user",
                    email=f"{role}@example.com",
                    password="StrongPassword@123",
                    role=role,
                )

                request = self.factory.get("/test/")
                request.user = user

                has_permission = self.permission.has_permission(
                    request,
                    view=None,
                )

                self.assertFalse(has_permission)

    def test_anonymous_user_does_not_have_permission(self):
        request = self.factory.get("/test/")
        request.user = AnonymousUser()

        has_permission = self.permission.has_permission(
            request,
            view=None,
        )

        self.assertFalse(has_permission)


class IsAdminOrManagerRoleTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = IsAdminOrManagerRole()

    def test_admin_and_manager_have_permission(self):
        for role in ["admin", "manager"]:
            with self.subTest(role=role):
                user = User.objects.create_user(
                    username=f"{role}_allowed_user",
                    email=f"{role}_allowed@example.com",
                    password="StrongPassword@123",
                    role=role,
                )

                request = self.factory.get("/test/")
                request.user = user

                has_permission = self.permission.has_permission(
                    request,
                    view=None,
                )

                self.assertTrue(has_permission)

    def test_agent_and_customer_do_not_have_permission(self):
        for role in ["agent", "customer"]:
            with self.subTest(role=role):
                user = User.objects.create_user(
                    username=f"{role}_denied_user",
                    email=f"{role}_denied@example.com",
                    password="StrongPassword@123",
                    role=role,
                )

                request = self.factory.get("/test/")
                request.user = user

                has_permission = self.permission.has_permission(
                    request,
                    view=None,
                )

                self.assertFalse(has_permission)

    def test_anonymous_user_does_not_have_permission(self):
        request = self.factory.get("/test/")
        request.user = AnonymousUser()

        has_permission = self.permission.has_permission(
            request,
            view=None,
        )

        self.assertFalse(has_permission)