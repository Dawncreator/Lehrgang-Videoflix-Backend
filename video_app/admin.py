from django.contrib import admin
from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "created_at", "thumbnail_url")
    list_filter = ("category", "created_at")
    search_fields = ("title", "description")
    readonly_fields = ("created_at", "thumbnail_url")

    fieldsets = (
        (
            "Video metadata",
            {
                "fields": (
                    "title",
                    "description",
                    "category",
                    "video_file",
                )
            },
        ),
        (
            "Generated data",
            {
                "fields": (
                    "thumbnail_url",
                )
            }
        ),
        (
            "Timestamps",
            {"fields": ("created_at",)},
        ),
    )
