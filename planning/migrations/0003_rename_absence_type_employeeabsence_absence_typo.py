# Generated by Django 3.2.22 on 2024-06-18 14:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0002_auto_20240618_1630'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employeeabsence',
            old_name='absence_type',
            new_name='absence_typo',
        ),
    ]
