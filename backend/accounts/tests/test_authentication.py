from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase


User = get_user_model()


class AuthenticationTests(APITestCase):
    def test_user_registration(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "test_user",
                "email": "test@example.com",
                "password": "StrongPassword@123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            User.objects.filter(username="test_user").exists()
        )

    def test_jwt_login(self):
        User.objects.create_user(
            username="login_user",
            email="login@example.com",
            password="StrongPassword@123",
        )

        response = self.client.post(
            "/api/auth/token/",
            {
                "username": "login_user",
                "password": "StrongPassword@123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_profile_requires_authentication(self):
        response = self.client.get("/api/auth/profile/")

        self.assertEqual(response.status_code, 401)

    def test_profile_with_authentication(self):
        User.objects.create_user(
            username="profile_user",
            email="profile@example.com",
            password="StrongPassword@123",
        )

        response = self.client.post(
            "/api/auth/token/",
            {
                "username": "profile_user",
                "password": "StrongPassword@123",
            },
            format="json",
        )

        access_token = response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        profile_response = self.client.get(
            "/api/auth/profile/"
        )

        self.assertEqual(profile_response.status_code, 200)
        self.assertEqual(
            profile_response.data["username"],
            "profile_user",
        )
        self.assertEqual(
            profile_response.data["email"],
            "profile@example.com",
        )
        self.assertEqual(
            profile_response.data["role"],
            "customer",
        )

    def test_duplicate_username_registration(self):
        User.objects.create_user(
            username="existing_user",
            email="existing@example.com",
            password="StrongPassword@123",
        )

        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "existing_user",
                "email": "new@example.com",
                "password": "StrongPassword@123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_duplicate_email_registration(self):
        User.objects.create_user(
            username="email_user",
            email="same@example.com",
            password="StrongPassword@123",
        )

        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "another_user",
                "email": "same@example.com",
                "password": "StrongPassword@123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_weak_password_registration(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "weak_user",
                "email": "weak@example.com",
                "password": "123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_jwt_login_with_invalid_password(self):
        User.objects.create_user(
            username="invalid_login_user",
            email="invalid@example.com",
            password="StrongPassword@123",
        )

        response = self.client.post(
            "/api/auth/token/",
            {
                "username": "invalid_login_user",
                "password": "WrongPassword@123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)

    def test_jwt_refresh_token(self):
        User.objects.create_user(
            username="refresh_user",
            email="refresh@example.com",
            password="StrongPassword@123",
        )

        login_response = self.client.post(
            "/api/auth/token/",
            {
                "username": "refresh_user",
                "password": "StrongPassword@123",
            },
            format="json",
        )

        refresh_token = login_response.data["refresh"]

        refresh_response = self.client.post(
            "/api/auth/token/refresh/",
            {
                "refresh": refresh_token,
            },
            format="json",
        )

        self.assertEqual(refresh_response.status_code, 200)
        self.assertIn("access", refresh_response.data)