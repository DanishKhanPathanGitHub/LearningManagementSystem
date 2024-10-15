# Generated by Django 5.1.1 on 2024-09-21 01:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_remove_userprofile_country'),
        ('classroom', '0048_remove_announcement_read_status_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignmentsubmission',
            name='student',
        ),
        migrations.AddField(
            model_name='assignmentsubmission',
            name='student',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='students_submissions', to='accounts.userprofile'),
            preserve_default=False,
        ),
    ]
