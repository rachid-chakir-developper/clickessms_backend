# Generated by Django 3.2.22 on 2023-12-07 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('human_ressources', '0005_auto_20231024_1233'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='current_latitude',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='current_longitude',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
