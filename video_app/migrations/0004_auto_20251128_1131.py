from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video_app', '0003_alter_video_thumbnail_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='thumbnail_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
