from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    """
    Configuration class for the authentication application.

    This config defines metadata for the `auth_app` Django application and is
    automatically loaded by Django when the project starts. It ensures that the
    app is correctly registered within the project's application registry.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_app'
