# Generated by Django 5.0.3 on 2024-04-11 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0029_alter_assignment_due_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='class/announcements'),
        ),
    ]