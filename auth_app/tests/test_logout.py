from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from auth_app.api import utils


class LogoutEndpointTests(APITestCase):
    """
    Tests for the logout endpoint.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="logout@example.com",
            email="logout@example.com",
            password="Test12345",
            is_active=True
        )
        access, refresh = utils.generate_jwt_tokens(self.user)

        self.access_token = access
        self.refresh_token = refresh

    def test_logout_success(self):
        url = reverse("api-logout")

        self.client.cookies["access_token"] = self.access_token
        self.client.cookies["refresh_token"] = self.refresh_token

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["detail"],
            "Logout successful! All tokens will be deleted. Refresh token is now invalid."
        )

        self.assertIn(self.refresh_token, utils.token_blacklist)

    def test_logout_missing_token(self):
        url = reverse("api-logout")

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
