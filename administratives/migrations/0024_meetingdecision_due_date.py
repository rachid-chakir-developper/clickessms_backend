# Generated by Django 3.2.22 on 2024-05-23 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administratives', '0023_rename_points_to_review_meetingreviewpoint_point_to_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='meetingdecision',
            name='due_date',
            field=models.DateTimeField(null=True),
        ),
    ]
