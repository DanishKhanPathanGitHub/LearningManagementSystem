# Generated by Django 5.1.1 on 2024-09-29 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0056_lecture_blog_quiz_quizoptions_section_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lecture',
            name='order',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='section',
            name='order',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterUniqueTogether(
            name='lecture',
            unique_together={('section', 'order')},
        ),
        migrations.AlterUniqueTogether(
            name='section',
            unique_together={('classroom', 'order')},
        ),
    ]
