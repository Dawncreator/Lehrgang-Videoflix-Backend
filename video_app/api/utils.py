from video_app.models import Video
import os
from django.http import FileResponse, Http404


def get_all_videos():
    """
    Return all videos ordered by creation date (DESC).
    """
    return Video.objects.all()


def get_hls_playlist_path(movie_id: int, resolution: str) -> str:
    """
    Build absolute path to HLS playlist file.
    media/hls/<movie_id>/<resolution>/index.m3u8
    """
    base = "media/hls"
    return os.path.join(base, str(movie_id), resolution, "index.m3u8")


def load_hls_playlist(movie_id: int, resolution: str) -> FileResponse:
    """
    Load HLS playlist file or raise 404.
    """
    playlist_path = get_hls_playlist_path(movie_id, resolution)

    if not os.path.exists(playlist_path):
        raise Http404("Playlist not found.")

    return FileResponse(open(playlist_path, "rb"), content_type="application/vnd.apple.mpegurl")


def get_hls_segment_path(movie_id, resolution, segment):
    """
    Build absolute filesystem path for one HLS .ts segment.
    """
    base = os.path.join("media", "hls", str(movie_id), resolution)
    return os.path.join(base, segment)


def load_hls_segment(movie_id, resolution, segment):
    """
    Return a FileResponse with the TS segment or raise 404.
    """
    file_path = get_hls_segment_path(movie_id, resolution, segment)

    if not os.path.exists(file_path):
        raise Http404("Segment not found.")

    return FileResponse(
        open(file_path, "rb"),
        content_type="video/MP2T"
    )
