# Generated by Django 3.2.22 on 2024-03-18 13:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qualities', '0007_auto_20240318_1437'),
    ]

    operations = [
        migrations.RenameField(
            model_name='undesirableevent',
            old_name='undesirable_event_normal_type',
            new_name='undesirable_event_normal_types',
        ),
        migrations.RenameField(
            model_name='undesirableevent',
            old_name='undesirable_event_serious_type',
            new_name='undesirable_event_serious_types',
        ),
    ]
