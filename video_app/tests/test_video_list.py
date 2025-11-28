import pytest
from django.urls import reverse
from video_app.models import Video


@pytest.mark.django_db
class TestVideoListEndpoint:

    def test_video_list_empty(self, client):
        response = client.get("/api/video/")
        assert response.status_code == 200
        assert response.json() == []

    def test_video_list_with_entries(self, client):
        Video.objects.create(
            title="Test",
            description="Desc",
            category="test",
        )

        response = client.get("/api/video/")
        data = response.json()

        assert response.status_code == 200
        assert len(data) == 1
        assert data[0]["title"] == "Test"
        assert data[0]["description"] == "Desc"
        assert data[0]["category"] == "test"
