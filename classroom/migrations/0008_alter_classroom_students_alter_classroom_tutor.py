# Generated by Django 5.0.3 on 2024-03-24 02:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_user_username'),
        ('classroom', '0007_alter_classroom_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classroom',
            name='students',
            field=models.ManyToManyField(related_name='classroom_students', to='accounts.userprofile'),
        ),
        migrations.AlterField(
            model_name='classroom',
            name='tutor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classroom_tutor', to='accounts.userprofile'),
        ),
    ]
