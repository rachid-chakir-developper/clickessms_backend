# Generated by Django 3.2.22 on 2024-05-21 14:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('human_ressources', '0032_auto_20240521_1603'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employeecontract',
            old_name='ending_date_time',
            new_name='ending_date',
        ),
        migrations.RenameField(
            model_name='employeecontract',
            old_name='starting_date_time',
            new_name='starting_date',
        ),
    ]
