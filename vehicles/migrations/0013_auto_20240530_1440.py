# Generated by Django 3.2.22 on 2024-05-30 12:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('companies', '0025_activityauthorization_temporary_capacity'),
        ('human_ressources', '0037_employeecontract_folder'),
        ('vehicles', '0012_alter_vehicle_crit_air_vignette'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicleemployee',
            name='employees',
            field=models.ManyToManyField(to='human_ressources.Employee'),
        ),
        migrations.AlterField(
            model_name='vehicleemployee',
            name='vehicle',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vehicle_employees', to='vehicles.vehicle'),
        ),
        migrations.AlterField(
            model_name='vehicleestablishment',
            name='establishments',
            field=models.ManyToManyField(to='companies.Establishment'),
        ),
        migrations.AlterField(
            model_name='vehicleestablishment',
            name='vehicle',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vehicle_establishments', to='vehicles.vehicle'),
        ),
        migrations.CreateModel(
            name='VehicleOwnership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ownership_type', models.CharField(choices=[('PURCHASE', 'Purchase'), ('LEASE', 'Lease'), ('SALE', 'Sale')], max_length=10)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('purchase_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('lease_start_date', models.DateField(blank=True, null=True)),
                ('lease_duration_months', models.PositiveIntegerField(blank=True, null=True)),
                ('lease_end_date', models.DateField(blank=True, null=True)),
                ('expected_mileage', models.PositiveIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('vehicle', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vehicle_ownerships', to='vehicles.vehicle')),
            ],
        ),
    ]