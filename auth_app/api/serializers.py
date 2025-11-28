from django.contrib.auth import get_user_model
from rest_framework import serializers
from . import utils

User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    """
    Serializer handling input validation for user registration.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        """
        Ensure email is unique.
        """
        utils.raise_if_email_exists(value)
        return utils.normalize_email(value)

    def validate(self, attrs):
        """
        Validate matching passwords.
        """
        utils.raise_if_password_mismatch(
            attrs.get("password"),
            attrs.get("confirmed_password"),
        )
        return attrs

    def create(self, validated_data):
        """
        Create inactive user.
        """
        return utils.create_inactive_user(
            validated_data["email"],
            validated_data["password"],
        )


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user model.
    """

    class Meta:
        model = User
        fields = ["id", "email"]


class LoginSerializer(serializers.Serializer):
    """
    Serializer validating login input.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        from . import utils

        user = utils.authenticate_user(
            attrs.get("email"),
            attrs.get("password")
        )
        attrs["user"] = user
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for password reset request.
    """

    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Normalize email; do not reveal existence.
        """
        return utils.normalize_email(value)


class PasswordConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming a new password.
    """

    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        Ensure passwords match.
        """
        utils.raise_if_password_mismatch(
            attrs.get("new_password"),
            attrs.get("confirm_password"),
        )
        return attrs
