# Generated by Django 5.1.1 on 2024-09-28 14:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0054_alter_notification_timestamp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playlist',
            name='classroom',
        ),
        migrations.RemoveField(
            model_name='videolecture',
            name='playlist',
        ),
        migrations.DeleteModel(
            name='LectureNote',
        ),
        migrations.DeleteModel(
            name='Playlist',
        ),
        migrations.DeleteModel(
            name='VideoLecture',
        ),
    ]
