# Generated by Django 3.2.22 on 2024-03-28 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administratives', '0007_letter_letterbeneficiary'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='video_call_link',
            field=models.URLField(max_length=255, null=True),
        ),
    ]
