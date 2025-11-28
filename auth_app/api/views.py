from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    RegistrationSerializer,
    UserSerializer,
    LoginSerializer,
    PasswordResetSerializer,
    PasswordConfirmSerializer,
)
from . import utils

from .utils import activate_user_account
from .utils import generate_jwt_tokens
from django.contrib.auth.tokens import default_token_generator


class RegisterView(APIView):
    """
    Handle API user registration.
    """

    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return self._error_response()
        user = serializer.save()
        token = utils.generate_activation_token(user)
        uid = utils.build_uid(user)
        utils.send_activation_email(user, uid, token)
        body = utils.build_registration_response(user, token)
        return Response(body, status=status.HTTP_201_CREATED)

    @staticmethod
    def _error_response():
        """
        Return a generic error response.
        """
        return Response(
            {"detail": "Please check your input and try again."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserActivationView(APIView):
    """Activate a user account through uid and token."""

    def get(self, request, uidb64: str, token: str):
        """
        Handle GET request for account activation.

        Args:
            request: HTTP request object.
            uidb64 (str): Base64 user ID.
            token (str): Activation token.

        Returns:
            Response: JSON response with activation status.
        """
        activation_successful = activate_user_account(uidb64, token)

        if activation_successful:
            return Response(
                {"message": "Account successfully activated."},
                status=status.HTTP_200_OK
            )

        return Response(
            {"message": "Activation failed."},
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
    """
    Handle user login and set HttpOnly cookies.
    """

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        access, refresh = generate_jwt_tokens(user)

        response = Response({
            "detail": "Login successful",
            "user": {
                "id": user.id,
                "username": user.email
            }
        })

        response.set_cookie(
            key="access_token",
            value=access,
            httponly=True,
            secure=False,
            samesite="Lax",
            path="/"
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh,
            httponly=True,
            secure=False,
            samesite="Lax",
            path="/"
        )

        return response


class LogoutView(APIView):
    """
    Handle user logout by removing cookies and blacklisting refresh token.
    """

    def post(self, request):
        refresh = request.COOKIES.get("refresh_token")

        if not refresh:
            return Response(
                {"detail": "Please check your input and try again."},
                status=status.HTTP_400_BAD_REQUEST
            )

        utils.blacklist_refresh_token(refresh)

        response = Response(
            {
                "detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."
            },
            status=status.HTTP_200_OK
        )

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response


class RefreshTokenView(APIView):
    """
    Handle refreshing of access tokens using a valid refresh token.
    """

    def post(self, request):
        refresh = request.COOKIES.get("refresh_token")

        if not refresh:
            return Response(
                {"detail": "Please check your input and try again."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if utils.is_token_blacklisted(refresh):
            return Response(
                {"detail": "Unauthorized."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        payload = utils.decode_refresh_token(refresh)
        if not payload:
            return Response(
                {"detail": "Unauthorized."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user_id = payload.get("user_id")
        user = utils.User.objects.get(pk=user_id)

        new_access, _ = utils.generate_jwt_tokens(user)

        response = Response(
            {
                "detail": "Token refreshed",
                "access": new_access
            },
            status=status.HTTP_200_OK
        )

        response.set_cookie(
            key="access_token",
            value=new_access,
            httponly=True,
            secure=False,
            samesite="Lax",
            path="/"
        )

        return response


class PasswordResetView(APIView):
    """
    Handle password reset request.
    """

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = utils.User.objects.filter(email__iexact=email).first()

        # For security reasons: always same response
        if user:
            uid = utils.build_uid(user)
            token = default_token_generator.make_token(user)
            reset_link = utils.build_password_reset_link(uid, token)

            # WICHTIG: Nur diese 2 Parameter
            utils.send_password_reset_email(user, reset_link)

        return Response(
            {"detail": "An email has been sent to reset your password."},
            status=status.HTTP_200_OK,
        )


class PasswordConfirmView(APIView):
    """
    Confirm new password using uid and token.
    """

    def post(self, request, uidb64, token):
        serializer = PasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_password = serializer.validated_data["new_password"]

        success = utils.reset_user_password(uidb64, token, new_password)

        if not success:
            return Response(
                {"detail": "Please check your input and try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Your Password has been successfully reset."},
            status=status.HTTP_200_OK,
        )
