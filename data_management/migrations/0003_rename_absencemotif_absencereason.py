# Generated by Django 3.2.22 on 2024-03-15 09:28

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('data_management', '0002_absencemotif'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AbsenceMotif',
            new_name='AbsenceReason',
        ),
    ]
