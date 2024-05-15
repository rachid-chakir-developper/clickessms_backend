# Generated by Django 3.2.22 on 2024-05-10 09:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('data_management', '0016_establishmentservicetype'),
        ('medias', '0010_auto_20240201_1012'),
        ('sales', '0006_alter_client_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='EstablishmentService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(editable=False, max_length=255, null=True)),
                ('name', models.CharField(max_length=255)),
                ('theoretical_activity_days_number', models.FloatField(default=0, null=True)),
                ('theoretical_capacity', models.FloatField(default=0, null=True)),
                ('actual_capacity', models.FloatField(default=0, null=True)),
                ('description', models.TextField(default='', null=True)),
                ('observation', models.TextField(default='', null=True)),
                ('is_active', models.BooleanField(default=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='establishment_service_former', to=settings.AUTH_USER_MODEL)),
                ('image', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='establishment_service_image', to='medias.file')),
                ('service_type', models.ManyToManyField(related_name='establishment_service_types', to='data_management.EstablishmentServiceType')),
            ],
        ),
    ]
