# Generated by Django 3.2.22 on 2024-05-31 10:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0020_auto_20240531_1215'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vehicleinspection',
            old_name='is_body_condition_ok',
            new_name='is_body_condition_checked',
        ),
        migrations.RenameField(
            model_name='vehicleinspection',
            old_name='is_brake_fluid_level_ok',
            new_name='is_brake_fluid_level_checked',
        ),
        migrations.RenameField(
            model_name='vehicleinspection',
            old_name='is_coolant_level_ok',
            new_name='is_coolant_level_checked',
        ),
        migrations.RenameField(
            model_name='vehicleinspection',
            old_name='is_oil_level_ok',
            new_name='is_lights_condition_checked',
        ),
        migrations.RenameField(
            model_name='vehicleinspection',
            old_name='is_lights_condition_ok',
            new_name='is_oil_level_checked',
        ),
        migrations.RenameField(
            model_name='vehicleinspection',
            old_name='is_tire_pressure_ok',
            new_name='is_tire_pressure_checked',
        ),
        migrations.RenameField(
            model_name='vehicleinspection',
            old_name='is_windshield_washer_level_ok',
            new_name='is_windshield_washer_level_checked',
        ),
    ]