from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import StudentProfile


PASSWORD = "Neuro!2026pass"


class AuthTests(APITestCase):
    """Registration, login and the /me endpoint."""

    def register(self, **overrides):
        data = {
            "username": "maya",
            "email": "maya@example.com",
            "password": PASSWORD,
            "password2": PASSWORD,
            "institution": "Far Western University",
        }
        data.update(overrides)
        return self.client.post("/api/auth/register/", data, format="json")

    def test_register_creates_user_and_profile(self):
        response = self.register()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="maya")
        self.assertEqual(user.student_profile.institution, "Far Western University")
        # The password must never be sent back to the client
        self.assertNotIn("password", response.data)

    def test_register_rejects_mismatched_passwords(self):
        response = self.register(password2="Different!2026")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password2", response.data)
        self.assertFalse(User.objects.exists())

    def test_register_rejects_duplicate_email(self):
        self.register()
        response = self.register(username="maya2", email="MAYA@example.com")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_login_with_email_returns_tokens(self):
        self.register()
        response = self.client.post(
            "/api/auth/login/",
            {"username": "maya@example.com", "password": PASSWORD},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_with_wrong_password_is_rejected(self):
        self.register()
        response = self.client.post(
            "/api/auth/login/",
            {"username": "maya@example.com", "password": "wrong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_requires_login(self):
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_current_user_with_profile(self):
        user = User.objects.create_user("maya", "maya@example.com", PASSWORD)
        StudentProfile.objects.create(user=user, institution="FWU")
        self.client.force_authenticate(user=user)

        response = self.client.get("/api/auth/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "maya@example.com")
        self.assertEqual(response.data["institution"], "FWU")