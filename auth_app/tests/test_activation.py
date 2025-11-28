import json
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from rest_framework.test import APITestCase
from rest_framework import status


class ActivationEndpointTests(APITestCase):
    """Tests for the account activation endpoint."""

    def test_activation_success(self):
        """Test successful account activation."""
        user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="supersecret123",
            is_active=False
        )

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        url = reverse("api-activate",
                      kwargs={"uidb64": uidb64, "token": token})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"],
            "Account successfully activated."
        )

    def test_activation_failure(self):
        """Test activation with invalid token."""
        user = User.objects.create_user(
            username="test2@example.com",
            email="test2@example.com",
            password="supersecret123",
            is_active=False
        )

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        invalid_token = "invalid-token-string"

        url = reverse("api-activate",
                      kwargs={"uidb64": uidb64, "token": invalid_token})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["message"],
            "Activation failed."
        )
