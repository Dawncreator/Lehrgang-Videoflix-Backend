from django.urls import path
from .views import (
    RegisterView,
    UserActivationView,
    LoginView,
    LogoutView,
    RefreshTokenView,
    PasswordResetView,
    PasswordConfirmView,
)

"""
URL configuration for the authentication API.

This module maps all authentication-related endpoints to their corresponding
class-based views, including:

- user registration
- account activation
- login via JWT HttpOnly cookies
- logout and token invalidation
- access-token refresh using refresh-token cookies
- password-reset request
- password reset confirmation

All routes defined here must match the exact endpoint naming required by the
project specification and automated test suite.
"""

urlpatterns = [
    path("api/register/", RegisterView.as_view(), name="api-register"),
    path(
        "api/activate/<uidb64>/<token>/",
        UserActivationView.as_view(),
        name="api-activate",
    ),
    path("api/login/", LoginView.as_view(), name="api-login"),
    path("api/logout/", LogoutView.as_view(), name="api-logout"),
    path(
        "api/token/refresh/",
        RefreshTokenView.as_view(),
        name="api-token-refresh",
    ),
    path(
        "api/password_reset/",
        PasswordResetView.as_view(),
        name="api-password-reset",
    ),
    path(
        "api/password_confirm/<uidb64>/<token>/",
        PasswordConfirmView.as_view(),
        name="api-password-confirm",
    ),
]
