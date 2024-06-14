# Generated by Django 3.2.22 on 2024-06-04 09:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0026_auto_20240530_1515'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('medias', '0011_file_company'),
        ('vehicles', '0029_auto_20240603_1154'),
    ]

    operations = [
        migrations.CreateModel(
            name='VehicleTechnicalInspection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(editable=False, max_length=255, null=True)),
                ('inspection_date_time', models.DateTimeField(blank=True, null=True)),
                ('next_inspection_date', models.DateTimeField(blank=True, null=True)),
                ('observation', models.TextField(blank=True, default='', null=True)),
                ('state', models.CharField(choices=[('FAVORABLE', 'Favorable'), ('NOT_FAVORABLE', 'Non favorable')], default='FAVORABLE', max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vehicle_technical_inspections', to='companies.company')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('document', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vehicle_technical_inspections', to='medias.file')),
                ('folder', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='medias.folder')),
                ('vehicle', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vehicle_technical_inspections', to='vehicles.vehicle')),
            ],
        ),
    ]