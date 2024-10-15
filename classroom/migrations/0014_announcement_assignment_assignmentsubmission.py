# Generated by Django 5.0.3 on 2024-03-24 14:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_user_username'),
        ('classroom', '0013_alter_classroom_code_alter_classroom_password'),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('content', models.TextField()),
                ('classroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classroom.classroom')),
            ],
            options={
                'verbose_name': 'announcement',
                'verbose_name_plural': 'announcements',
            },
        ),
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('assignment', models.FileField(null=True, upload_to='class/assignments')),
                ('assigned_date', models.DateField(auto_now_add=True)),
                ('due_date', models.DateField()),
                ('classroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classroom.classroom')),
            ],
            options={
                'verbose_name': 'Assignment',
                'verbose_name_plural': 'Assignments',
            },
        ),
        migrations.CreateModel(
            name='AssignmentSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('file', models.FileField(null=True, upload_to='class/assignments')),
                ('upload_date', models.DateField(auto_now_add=True)),
                ('student', models.ManyToManyField(related_name='students_submissions', to='accounts.userprofile')),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classroom.assignment')),
            ],
            options={
                'verbose_name': 'AssignmentSubmissions',
                'verbose_name_plural': 'AssignmentsSubmissions',
            },
        ),
    ]
