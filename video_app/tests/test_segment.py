import os
import pytest
from django.conf import settings


@pytest.mark.django_db
class HLSSegmentEndpointTests:

    def test_segment_not_found(self, client):
        url = "/api/video/1/720p/0000.ts"
        response = client.get(url)
        assert response.status_code == 404

    def test_segment_success(self, client):
        base = os.path.join(settings.MEDIA_ROOT, "hls", "1", "720p")
        os.makedirs(base, exist_ok=True)
        seg_path = os.path.join(base, "0001.ts")

        with open(seg_path, "wb") as f:
            f.write(b"dummy")

        url = "/api/video/1/720p/0001.ts"
        response = client.get(url)

        assert response.status_code == 200
        assert response["Content-Type"] in ["video/mp2t",
                                            "application/octet-stream"]
