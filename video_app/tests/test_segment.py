import os
from django.urls import reverse
from django.conf import settings
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


class HLSSegmentEndpointTests(APITestCase):
    """
    Tests for single HLS TS segment.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            username="test@example.com",
            password="pass1234",
            is_active=True
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.movie_id = 1
        self.res = "480p"
        self.segment = "0001.ts"

        self.dir_path = os.path.join(
            settings.MEDIA_ROOT,
            "hls",
            str(self.movie_id),
            self.res
        )
        os.makedirs(self.dir_path, exist_ok=True)

        self.file_path = os.path.join(self.dir_path, self.segment)
        with open(self.file_path, "wb") as f:
            f.write(b"FAKE TS DATA")

    def test_segment_success(self):
        url = reverse(
            "api-hls-segment",
            args=[self.movie_id, self.res, self.segment]
        )
        response = self.client.get(url)

        assert response.status_code == 200
        assert response["Content-Type"] == "video/MP2T"

    def test_segment_not_found(self):
        url = reverse(
            "api-hls-segment",
            args=[99, "480p", "nope.ts"]
        )
        response = self.client.get(url)

        assert response.status_code == 404
