# Generated by Django 3.2.22 on 2024-03-18 11:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qualities', '0003_undesirableevent_employee'),
    ]

    operations = [
        migrations.RenameField(
            model_name='undesirableeventbeneficiary',
            old_name='undesirable',
            new_name='undesirable_event',
        ),
    ]
