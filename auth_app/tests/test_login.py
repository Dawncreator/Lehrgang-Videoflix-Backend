from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status


class LoginEndpointTests(APITestCase):
    """Tests for login endpoint."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="login@example.com",
            email="login@example.com",
            password="Test12345",
            is_active=True
        )

    def test_login_success(self):
        url = reverse("api-login")
        response = self.client.post(url, {
            "email": "login@example.com",
            "password": "Test12345"
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        self.assertEqual(response.data["detail"], "Login successful")

    def test_login_failure(self):
        url = reverse("api-login")
        response = self.client.post(url, {
            "email": "login@example.com",
            "password": "falsch"
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
