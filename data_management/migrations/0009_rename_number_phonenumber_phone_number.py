# Generated by Django 3.2.22 on 2024-04-02 09:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0008_auto_20240402_1100'),
    ]

    operations = [
        migrations.RenameField(
            model_name='phonenumber',
            old_name='number',
            new_name='phone_number',
        ),
    ]