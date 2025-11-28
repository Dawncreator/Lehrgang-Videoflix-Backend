from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from auth_app.api import utils


class RefreshTokenTests(APITestCase):
    """Tests for token refresh endpoint."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="refresh@example.com",
            email="refresh@example.com",
            password="Test12345",
            is_active=True
        )

        self.access, self.refresh = utils.generate_jwt_tokens(self.user)

    def test_refresh_success(self):
        url = reverse("api-token-refresh")

        self.client.cookies["refresh_token"] = self.refresh

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Token refreshed")
        self.assertIn("access_token", response.cookies)

    def test_refresh_missing_token(self):
        url = reverse("api-token-refresh")

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_invalid_token(self):
        url = reverse("api-token-refresh")

        self.client.cookies["refresh_token"] = "INVALID_TOKEN_123"

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
