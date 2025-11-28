import os
from django.http import FileResponse, Http404, JsonResponse
from django.conf import settings
from rest_framework.views import APIView
from video_app.models import Video


class VideoListAPIView(APIView):
    """
    GET /api/video/
    Returns all videos in the JSON format expected by the frontend.
    """

    def get(self, request):
        videos = Video.objects.all()
        data = []

        for v in videos:
            data.append({
                "id": v.id,
                "title": v.title,
                "description": v.description,
                "category": v.category,
                "created_at": v.created_at.isoformat(),
                "thumbnail_url": request.build_absolute_uri(v.thumbnail_url),
                "video_file": v.video_file.url if v.video_file else None,
            })

        return JsonResponse(data, safe=False)


def serve_hls_playlist(request, video_id, resolution):
    """
    Serves HLS master/playlists from:
    MEDIA_ROOT/hls/<id>/<resolution>/index.m3u8
    """

    playlist_path = os.path.join(
        settings.MEDIA_ROOT,
        "hls",
        str(video_id),
        resolution,
        "index.m3u8"
    )

    if not os.path.exists(playlist_path):
        raise Http404("Playlist not found")

    return FileResponse(open(playlist_path, "rb"), content_type="application/x-mpegURL")


def serve_hls_segment(request, video_id, resolution, segment):
    """
    Serves .ts segments from:
    MEDIA_ROOT/hls/<id>/<resolution>/<segment>.ts
    """

    segment_path = os.path.join(
        settings.MEDIA_ROOT,
        "hls",
        str(video_id),
        resolution,
        f"{segment}.ts"
    )

    if not os.path.exists(segment_path):
        raise Http404("Segment not found")

    return FileResponse(open(segment_path, "rb"), content_type="video/mp2t")
