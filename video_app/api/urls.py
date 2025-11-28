from django.urls import path, re_path
from .views import VideoListAPIView, serve_hls_playlist, serve_hls_segment

urlpatterns = [

    path("", VideoListAPIView.as_view()),

    re_path(
        r"^(?P<video_id>\d+)/(?P<resolution>[0-9]{3,4}p)/index\.m3u8$",
        serve_hls_playlist,
        name="hls_playlist"
    ),

    re_path(
        r"^(?P<video_id>\d+)/(?P<resolution>[0-9]{3,4}p)/(?P<segment>[0-9]{4})\.ts$",
        serve_hls_segment,
        name="hls_segment"
    ),
]
