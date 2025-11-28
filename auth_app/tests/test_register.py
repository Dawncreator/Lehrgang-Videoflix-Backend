import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_register_success():
    client = APIClient()
    url = reverse("api-register")
    payload = {
        "email": "user@example.com",
        "password": "securepassword",
        "confirmed_password": "securepassword",
    }
    response = client.post(url, payload, format="json")

    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == "user@example.com"
    assert "token" in data

    user = User.objects.get(email="user@example.com")
    assert user.is_active is False


@pytest.mark.django_db
def test_register_duplicate_email_error():
    User.objects.create_user(
        username="user@example.com",
        email="user@example.com",
        password="x",
    )
    client = APIClient()
    url = reverse("api-register")
    payload = {
        "email": "user@example.com",
        "password": "pw",
        "confirmed_password": "pw",
    }
    response = client.post(url, payload, format="json")

    assert response.status_code == 400
    assert response.json()[
        "detail"] == "Please check your input and try again."


@pytest.mark.django_db
def test_register_password_mismatch_error():
    client = APIClient()
    url = reverse("api-register")
    payload = {
        "email": "user2@example.com",
        "password": "pw",
        "confirmed_password": "nomatch",
    }
    response = client.post(url, payload, format="json")

    assert response.status_code == 400
    assert response.json()[
        "detail"] == "Please check your input and try again."
    assert not User.objects.filter(email="user2@example.com").exists()
