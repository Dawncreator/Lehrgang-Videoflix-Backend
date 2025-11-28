import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from video_app.models import Video
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestVideoListEndpoint:
    """
    Tests for Video List.
    """

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("api-video-list")

        self.user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="password123",
            is_active=True,
        )

        self.client.force_authenticate(self.user)

    def test_video_list_empty(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert response.json() == []

    def test_video_list_with_entries(self):
        Video.objects.create(
            title="Movie Title",
            description="Movie Description",
            thumbnail_url="http://example.com/image.jpg",
            category="Drama",
        )

        response = self.client.get(self.url)
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Movie Title"
        assert data[0]["category"] == "Drama"
