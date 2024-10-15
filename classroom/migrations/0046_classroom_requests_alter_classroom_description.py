# Generated by Django 5.1.1 on 2024-09-14 16:19

import tinymce.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_remove_userprofile_country'),
        ('classroom', '0045_alter_classroom_code_alter_classroom_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroom',
            name='requests',
            field=models.ManyToManyField(blank=True, related_name='classroom_requests', to='accounts.userprofile'),
        ),
        migrations.AlterField(
            model_name='classroom',
            name='description',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
    ]