# Generated by Django 5.1.1 on 2024-09-27 01:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0052_notification_assignment_notification_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='read',
            field=models.BooleanField(default=False),
        ),
    ]
