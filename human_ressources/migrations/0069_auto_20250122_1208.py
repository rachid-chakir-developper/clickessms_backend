# Generated by Django 3.2.22 on 2025-01-22 11:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('human_ressources', '0068_beneficiaryendowmententry'),
    ]

    operations = [
        migrations.RenameField(
            model_name='beneficiary',
            old_name='gender',
            new_name='genderh',
        ),
        migrations.RenameField(
            model_name='beneficiaryadmission',
            old_name='gender',
            new_name='genderh',
        ),
        migrations.RenameField(
            model_name='employee',
            old_name='gender',
            new_name='genderh',
        ),
    ]
