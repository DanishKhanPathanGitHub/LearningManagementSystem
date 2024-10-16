# Generated by Django 5.1.1 on 2024-09-16 04:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0047_alter_classroom_cover_pic'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='announcement',
            name='read_status',
        ),
        migrations.AlterField(
            model_name='assignment',
            name='assigned_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='assignmentsubmission',
            name='upload_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='videolecture',
            name='upload_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
