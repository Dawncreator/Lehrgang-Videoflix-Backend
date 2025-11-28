import os
import subprocess
from django.conf import settings
from django.core.files.storage import default_storage
from video_app.models import Video


def debug(msg: str):
    print(f"[TASK DEBUG] {msg}", flush=True)


def run_ffmpeg_command(command: list) -> None:
    debug(f"Running ffmpeg: {' '.join(command)}")

    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    if result.returncode != 0:
        error_text = result.stderr.decode()
        debug(f"FFmpeg ERROR: {error_text}")
        raise RuntimeError(
            f"FFmpeg failed: {' '.join(command)}\nError: {error_text}"
        )


def generate_thumbnail(video_id: int, input_path: str) -> str:
    debug(f"Generating thumbnail for video {video_id}")

    thumbnail_rel = f"thumbnails/{video_id}.jpg"
    thumbnail_abs = os.path.join(settings.MEDIA_ROOT, thumbnail_rel)

    os.makedirs(os.path.dirname(thumbnail_abs), exist_ok=True)

    ffmpeg_thumb_cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-ss", "00:00:01.000",
        "-vframes", "1",
        thumbnail_abs,
    ]

    run_ffmpeg_command(ffmpeg_thumb_cmd)

    debug(f"Thumbnail generated at {thumbnail_rel}")
    return thumbnail_rel


def convert_video_to_hls(video_id: int, video_file_path: str) -> None:
    debug(f"START HLS JOB for video {video_id}")

    resolutions = {
        "480p": "854x480",
        "720p": "1280x720",
        "1080p": "1920x1080",
    }

    input_path = os.path.join(settings.MEDIA_ROOT, video_file_path)

    if not default_storage.exists(video_file_path):
        debug("ERROR: input file not found.")
        raise FileNotFoundError(f"Video file not found: {input_path}")

    for res_name, res_size in resolutions.items():
        debug(f"Converting {video_id} → {res_name}")

        output_dir = os.path.join(
            settings.MEDIA_ROOT, "hls", str(video_id), res_name
        )
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, "index.m3u8")

        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-vf", f"scale={res_size}",
            "-c:v", "h264",
            "-c:a", "aac",
            "-f", "hls",
            "-hls_time", "4",
            "-hls_list_size", "0",
            "-hls_segment_filename",
            os.path.join(output_dir, "%04d.ts"),
            output_file,
        ]

        run_ffmpeg_command(ffmpeg_cmd)

    thumbnail_rel_path = generate_thumbnail(video_id, input_path)

    thumbnail_absolute_url = f"http://127.0.0.1:8000{settings.MEDIA_URL}{thumbnail_rel_path}"

    video = Video.objects.get(id=video_id)
    video.thumbnail_url = thumbnail_absolute_url
    video.save(update_fields=["thumbnail_url"])

    debug(f"Thumbnail URL saved: {video.thumbnail_url}")
