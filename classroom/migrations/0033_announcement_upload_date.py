# Generated by Django 5.0.3 on 2024-04-12 06:51

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0032_remove_announcement_read_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='upload_date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
