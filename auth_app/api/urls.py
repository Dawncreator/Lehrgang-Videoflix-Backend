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

urlpatterns = [
    path("register/", RegisterView.as_view(), name="api-register"),
    path("activate/<uidb64>/<token>/",
         UserActivationView.as_view(), name="api-activate"),
    path("login/", LoginView.as_view(), name="api-login"),
    path("logout/", LogoutView.as_view(), name="api-logout"),
    path("token/refresh/", RefreshTokenView.as_view(), name="api-token-refresh"),
    path("password_reset/", PasswordResetView.as_view(), name="api-password-reset"),
    path("password_confirm/<uidb64>/<token>/",
         PasswordConfirmView.as_view(), name="api-password-confirm"),
]
