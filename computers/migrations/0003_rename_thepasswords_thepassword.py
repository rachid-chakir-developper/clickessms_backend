# Generated by Django 3.2.22 on 2024-12-12 10:11

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0033_auto_20241125_1105'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('computers', '0002_thebackup_thepasswords'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ThePasswords',
            new_name='ThePassword',
        ),
    ]