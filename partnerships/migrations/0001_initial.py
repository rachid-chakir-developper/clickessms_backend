# Generated by Django 3.2.22 on 2024-01-10 09:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('medias', '0008_alter_folder_folder'),
    ]

    operations = [
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=255, null=True)),
                ('name', models.CharField(max_length=255)),
                ('partner_type', models.CharField(choices=[('BUSINESS', 'Entreprise'), ('INDIVIDUAL', 'Particulier')], default='INDIVIDUAL', max_length=50, null=True)),
                ('manager_name', models.CharField(max_length=255, null=True)),
                ('latitude', models.CharField(max_length=255, null=True)),
                ('longitude', models.CharField(max_length=255, null=True)),
                ('city', models.CharField(max_length=255, null=True)),
                ('country', models.CharField(max_length=255, null=True)),
                ('zip_code', models.CharField(max_length=255, null=True)),
                ('address', models.CharField(max_length=25, null=True)),
                ('mobile', models.CharField(max_length=255, null=True)),
                ('fix', models.CharField(max_length=255, null=True)),
                ('fax', models.CharField(max_length=255, null=True)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('web_site', models.URLField(max_length=255, null=True)),
                ('other_contacts', models.CharField(max_length=255, null=True)),
                ('iban', models.CharField(max_length=255, null=True)),
                ('bic', models.CharField(max_length=255, null=True)),
                ('bank_name', models.CharField(max_length=255, null=True)),
                ('description', models.TextField(default='', null=True)),
                ('observation', models.TextField(default='', null=True)),
                ('is_active', models.BooleanField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('cover_image', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='partner_cover_image', to='medias.file')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='partner_former', to=settings.AUTH_USER_MODEL)),
                ('photo', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='partner_photo', to='medias.file')),
            ],
        ),
    ]
