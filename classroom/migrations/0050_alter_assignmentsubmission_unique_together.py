# Generated by Django 5.1.1 on 2024-09-21 01:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_remove_userprofile_country'),
        ('classroom', '0049_remove_assignmentsubmission_student_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='assignmentsubmission',
            unique_together={('student', 'assignment')},
        ),
    ]
