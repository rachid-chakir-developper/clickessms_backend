# Generated by Django 3.2.22 on 2024-02-01 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0003_alter_vehicle_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='number',
            field=models.CharField(editable=False, max_length=255, null=True),
        ),
    ]
