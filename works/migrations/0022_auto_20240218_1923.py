# Generated by Django 3.2.22 on 2024-02-18 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('works', '0021_alter_task_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskchecklistitem',
            name='comment',
            field=models.TextField(default='', null=True),
        ),
        migrations.AddField(
            model_name='taskchecklistitem',
            name='localisation',
            field=models.CharField(max_length=255, null=True),
        ),
    ]