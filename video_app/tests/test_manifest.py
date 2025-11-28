import os
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

"""
Test suite for validating HLS playlist (index.m3u8) delivery.

This class ensures:
- authenticated users can access existing HLS manifest files
- a proper 404 response is returned when the requested file does not exist
- temporary HLS test directories are created and cleaned up automatically

The tests operate on a temporary `media/hls/...` directory structure and
simulate real requests to the HLS endpoint.
"""

User = get_user_model()


class HLSManifestTests:
    """
    Tests for the `/api/video/<movie_id>/<resolution>/index.m3u8` endpoint.

    The setup:
        - authenticates a test user
        - creates a temporary HLS folder and manifest file
    The teardown:
        - removes all test files and folders safely
    """

    def setup_method(self):
        """
        Prepare a valid user, authenticate the client, and create
        a temporary HLS directory with a minimal valid playlist file.
        """
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="test",
            email="test@example.com",
            password="12345678",
            is_active=True,
        )

        self.client.force_authenticate(self.user)

        os.makedirs("media/hls/1/720p", exist_ok=True)
        with open("media/hls/1/720p/index.m3u8", "w") as f:
            f.write("#EXTM3U")

    def teardown_method(self):
        """
        Remove all temporary files created during the test.
        Fail silently if some directories are already deleted.
        """
        try:
            os.remove("media/hls/1/720p/index.m3u8")
            os.rmdir("media/hls/1/720p")
            os.rmdir("media/hls/1")
            os.rmdir("media/hls")
        except Exception:
            pass

    def test_manifest_success(self):
        """
        Ensure an existing manifest file returns HTTP 200
        and contains valid M3U8 content.
        """
        response = self.client.get("/api/video/1/720p/index.m3u8")
        assert response.status_code == 200
        assert b"#EXTM3U" in response.content

    def test_manifest_not_found(self):
        """
        Ensure a non-existing manifest returns HTTP 404.
        """
        response = self.client.get("/api/video/999/480p/index.m3u8")
        assert response.status_code == 404
