"""
Utility functions for authentication logic.
"""

import os
from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.exceptions import ValidationError
from django.template.loader import render_to_string

User = get_user_model()


def normalize_email(email):
    """Normalize email to lowercase."""
    return email.strip().lower()


def raise_if_email_exists(email):
    """Raise a generic error if the email already exists."""
    normalized = normalize_email(email)
    if User.objects.filter(email__iexact=normalized).exists():
        raise ValidationError("Please check your input and try again.")


def raise_if_password_mismatch(password, confirmed):
    """Raise generic error if passwords differ."""
    if password != confirmed:
        raise ValidationError("Please check your input and try again.")


def create_inactive_user(email, password):
    """Create inactive Django user."""
    normalized = normalize_email(email)
    user = User.objects.create_user(
        username=normalized,
        email=normalized,
        password=password,
    )
    user.is_active = False
    user.save(update_fields=["is_active"])
    return user


def generate_activation_token(user):
    """Generate activation token."""
    return default_token_generator.make_token(user)


def build_uid(user):
    """Convert user id to uidb64 string."""
    return urlsafe_base64_encode(force_bytes(user.pk))


def build_activation_link(uid, token):
    """Build activation link pointing to frontend."""
    base = os.getenv("FRONTEND_BASE_URL", "http://localhost:4200")
    return f"{base}/activate/{uid}/{token}/"


def send_activation_email(user, uid: str, token: str) -> None:
    """
    Send activation email using HTML template.
    """
    link = build_activation_link(uid, token)
    subject = "Confirm your email"
    context = {"user": user, "activation_link": link}

    html_body = render_to_string("auth_app/activation_email.html", context)
    plain_body = (
        f"Dear {user.email},\n\n"
        f"Please activate your account using this link: {link}\n"
        "If you did not create an account with us, please disregard this email."
    )

    send_mail(
        subject,
        plain_body,
        getattr(settings, "DEFAULT_FROM_EMAIL", "info@videoflix.com"),
        [user.email],
        html_message=html_body,
        fail_silently=True,
    )


def build_registration_response(user, token):
    """Build the registration response JSON body."""
    return {
        "user": {"id": user.id, "email": user.email},
        "token": token,
    }


def activate_user_account(uidb64, token):
    """Validate activation token and activate the user account."""
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        return False

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=["is_active"])
        return True

    return False


def authenticate_user(email, password):
    """Authenticate user or raise generic validation error."""
    user = authenticate(username=email, password=password)
    if not user or not user.is_active:
        raise ValidationError("Please check your input and try again.")
    return user


def generate_jwt_tokens(user):
    """Generate access and refresh JWT tokens."""
    secret = settings.SECRET_KEY

    access_payload = {
        "user_id": user.id,
        "type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=15),
    }

    refresh_payload = {
        "user_id": user.id,
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=7),
    }

    access = jwt.encode(access_payload, secret, algorithm="HS256")
    refresh = jwt.encode(refresh_payload, secret, algorithm="HS256")
    return access, refresh


token_blacklist = set()


def blacklist_refresh_token(token: str) -> None:
    """
    Add a refresh token to the blacklist.
    """
    if token:
        token_blacklist.add(token)


def is_token_blacklisted(token: str) -> bool:
    """
    Check whether refresh token is blacklisted.
    """
    return token in token_blacklist


def decode_refresh_token(token: str):
    """
    Decode refresh token and validate it.
    Returns payload or None if invalid.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "refresh":
            return None
        return payload
    except Exception:
        return None


def build_password_reset_link(uid, token):
    """Build password reset link pointing to frontend."""
    base = os.getenv("FRONTEND_BASE_URL", "http://localhost:4200")
    return f"{base}/password-reset-confirm/{uid}/{token}/"


def send_password_reset_email(user, reset_link: str) -> None:
    """
    Send password reset email using HTML template.
    """
    subject = "Reset your password"
    context = {"reset_link": reset_link}

    html_body = render_to_string("auth_app/password_reset_email.html", context)
    plain_body = (
        "Hello,\n\n"
        f"You can reset your Videoflix password using this link: {reset_link}\n"
        "If you did not request a password reset, please ignore this email."
    )

    send_mail(
        subject,
        plain_body,
        getattr(settings, "DEFAULT_FROM_EMAIL", "info@videoflix.com"),
        [user.email],
        html_message=html_body,
        fail_silently=True,
    )


def reset_user_password(uidb64, token, new_password):
    """
    Validate reset token and set new password.

    Returns True if reset was successful, otherwise False.
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        return False

    if not default_token_generator.check_token(user, token):
        return False

    user.set_password(new_password)
    user.save(update_fields=["password"])
    return True
