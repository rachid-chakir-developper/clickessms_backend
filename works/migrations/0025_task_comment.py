# Generated by Django 3.2.22 on 2024-02-20 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('works', '0024_task_client_task_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='comment',
            field=models.TextField(default='', null=True),
        ),
    ]