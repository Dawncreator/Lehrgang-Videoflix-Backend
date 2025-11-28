from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


class PasswordResetTests(APITestCase):
    """Tests for password reset endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="pwreset@example.com",
            email="pwreset@example.com",
            password="OldPass123",
            is_active=True,
        )

    def test_password_reset_request_existing_email(self):
        url = reverse("api-password-reset")
        response = self.client.post(
            url,
            {"email": "pwreset@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["detail"],
            "An email has been sent to reset your password.",
        )

    def test_password_reset_request_unknown_email(self):
        url = reverse("api-password-reset")
        response = self.client.post(
            url,
            {"email": "unknown@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["detail"],
            "An email has been sent to reset your password.",
        )

    def test_password_confirm_success(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        url = reverse(
            "api-password-confirm",
            kwargs={"uidb64": uidb64, "token": token},
        )

        response = self.client.post(
            url,
            {
                "new_password": "NewPass123",
                "confirm_password": "NewPass123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["detail"],
            "Your Password has been successfully reset.",
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPass123"))

    def test_password_confirm_invalid_token(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        invalid_token = "invalid-token"

        url = reverse(
            "api-password-confirm",
            kwargs={"uidb64": uidb64, "token": invalid_token},
        )

        response = self.client.post(
            url,
            {
                "new_password": "NewPass123",
                "confirm_password": "NewPass123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
