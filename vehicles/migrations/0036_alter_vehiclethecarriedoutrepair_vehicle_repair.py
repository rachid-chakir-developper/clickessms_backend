# Generated by Django 3.2.22 on 2024-06-05 08:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0035_vehiclethecarriedoutrepair'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehiclethecarriedoutrepair',
            name='vehicle_repair',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='repairs', to='vehicles.vehiclerepair'),
        ),
    ]
