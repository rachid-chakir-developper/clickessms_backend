# Generated by Django 3.2.22 on 2024-05-20 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('works', '0028_auto_20240223_0944'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='is_deleted',
            field=models.BooleanField(default=False, null=True),
        ),
    ]