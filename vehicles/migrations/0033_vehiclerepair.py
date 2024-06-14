# Generated by Django 3.2.22 on 2024-06-04 14:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0026_auto_20240530_1515'),
        ('medias', '0011_file_company'),
        ('partnerships', '0008_auto_20240520_1043'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('vehicles', '0032_rename_failure_text_vehicleinspectionfailure_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='VehicleRepair',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(editable=False, max_length=255, null=True)),
                ('label', models.CharField(blank=True, max_length=255, null=True)),
                ('repair_date_time', models.DateTimeField(blank=True, null=True)),
                ('state', models.CharField(choices=[('COMPLETED', 'Terminé'), ('TO_DO', 'À faire')], default='COMPLETED', max_length=50, null=True)),
                ('description', models.TextField(blank=True, default='', null=True)),
                ('observation', models.TextField(blank=True, default='', null=True)),
                ('report', models.TextField(blank=True, default='', null=True)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vehicle_repairs', to='companies.company')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('document', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vehicle_repairs', to='medias.file')),
                ('folder', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='medias.folder')),
                ('garage_partner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vehicle_repairs', to='partnerships.partner')),
                ('vehicle', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vehicle_repairs', to='vehicles.vehicle')),
            ],
        ),
    ]