# Generated by Django 3.2.22 on 2024-05-20 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0005_vehicle_folder'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='is_deleted',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
