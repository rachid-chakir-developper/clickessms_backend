# Generated by Django 3.2.22 on 2025-03-10 08:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0006_jobposting'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobposting',
            name='is_published',
        ),
    ]
