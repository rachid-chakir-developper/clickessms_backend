# Generated by Django 3.2.22 on 2024-06-05 08:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('vehicles', '0036_alter_vehiclethecarriedoutrepair_vehicle_repair'),
    ]

    operations = [
        migrations.CreateModel(
            name='VehicleRepairVigilantPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(default='', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vehicle_repair_vigilant_points', to=settings.AUTH_USER_MODEL)),
                ('vehicle_repair', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vigilant_points', to='vehicles.vehiclerepair')),
            ],
        ),
    ]