# Generated by Django 5.0.3 on 2024-03-25 06:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0015_assignment_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='completed',
            field=models.BooleanField(default=False),
        ),
    ]