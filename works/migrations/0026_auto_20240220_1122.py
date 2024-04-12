# Generated by Django 3.2.22 on 2024-02-20 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('works', '0025_task_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='materials_infos',
            field=models.TextField(default='', null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='vehicles_infos',
            field=models.TextField(default='', null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='workers_infos',
            field=models.TextField(default='', null=True),
        ),
    ]