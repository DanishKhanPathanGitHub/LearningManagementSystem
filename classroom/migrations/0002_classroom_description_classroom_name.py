# Generated by Django 5.0.3 on 2024-03-24 01:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroom',
            name='description',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='classroom',
            name='name',
            field=models.CharField(max_length=50, null=True),
        ),
    ]