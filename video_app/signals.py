import os
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
import django_rq
from video_app.models import Video


@receiver(post_save, sender=Video)
def handle_video_upload(sender, instance, created, **kwargs):
    """
    Startet HLS-Konvertierung NUR wenn das Video NEU erstellt wurde.
    """

    if not instance.video_file:
        return

    if not created:
        return

    file_path = instance.video_file.name
    abs_path = os.path.join(settings.MEDIA_ROOT, file_path)

    if not os.path.exists(abs_path):
        return

    queue = django_rq.get_queue("default")
    queue.enqueue("video_app.tasks.convert_video_to_hls",
                  instance.id, file_path)

    print(f"[SIGNAL] Queued HLS job for video ID {instance.id}")
