# Generated by Django 3.2.22 on 2024-05-30 14:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0014_auto_20240530_1504'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vehicleownership',
            old_name='lease_end_date',
            new_name='lease_ending_date',
        ),
        migrations.RenameField(
            model_name='vehicleownership',
            old_name='lease_start_date',
            new_name='lease_starting_date',
        ),
    ]