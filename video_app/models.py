from django.db import models


class Video(models.Model):
    """
    Video metadata and optional source file for background conversion.
    """

    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail_url = models.URLField(
        blank=True,
        null=True,
        help_text="Wird vom FFmpeg-Worker automatisch gesetzt."
    )
    category = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    video_file = models.FileField(
        upload_to="videos/",
        blank=True,
        null=True,
        help_text="Optional source MP4 file for background conversion.",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.id})"
