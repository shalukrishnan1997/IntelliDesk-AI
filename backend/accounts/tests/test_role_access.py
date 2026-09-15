from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class UserListRoleAccessTests(APITestCase):
    endpoint = "/api/auth/users/"

    def test_admin_and_manager_can_access_user_list(self):
        for role in ["admin", "manager"]:
            with self.subTest(role=role):
                user = User.objects.create_user(
                    username=f"{role}_access_user",
                    email=f"{role}_access@example.com",
                    password="StrongPassword@123",
                    role=role,
                )

                self.client.force_authenticate(user=user)
                response = self.client.get(self.endpoint)

                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                )

                self.client.force_authenticate(user=None)

    def test_agent_and_customer_cannot_access_user_list(self):
        for role in ["agent", "customer"]:
            with self.subTest(role=role):
                user = User.objects.create_user(
                    username=f"{role}_blocked_user",
                    email=f"{role}_blocked@example.com",
                    password="StrongPassword@123",
                    role=role,
                )

                self.client.force_authenticate(user=user)
                response = self.client.get(self.endpoint)

                self.assertEqual(
                    response.status_code,
                    status.HTTP_403_FORBIDDEN,
                )

                self.client.force_authenticate(user=None)

    def test_anonymous_user_cannot_access_user_list(self):
        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )