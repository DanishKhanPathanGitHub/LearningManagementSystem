# Generated by Django 5.1.1 on 2024-10-04 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_remove_userprofile_country'),
        ('classroom', '0065_remove_comment_reply_comment_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='upvoted_student',
            field=models.ManyToManyField(related_name='upvoted_comments', to='accounts.userprofile'),
        ),
    ]
