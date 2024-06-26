# Generated by Django 3.2.22 on 2024-05-25 14:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('medias', '0011_file_company'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('companies', '0025_activityauthorization_temporary_capacity'),
    ]

    operations = [
        migrations.CreateModel(
            name='GovernanceMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(editable=False, max_length=255, null=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('position', models.CharField(max_length=255, null=True)),
                ('birth_date', models.DateTimeField(null=True)),
                ('hiring_date', models.DateTimeField(null=True)),
                ('probation_end_date', models.DateTimeField(null=True)),
                ('work_end_date', models.DateTimeField(null=True)),
                ('starting_salary', models.FloatField(null=True)),
                ('latitude', models.CharField(max_length=255, null=True)),
                ('longitude', models.CharField(max_length=255, null=True)),
                ('city', models.CharField(max_length=255, null=True)),
                ('country', models.CharField(max_length=255, null=True)),
                ('zip_code', models.CharField(max_length=255, null=True)),
                ('address', models.TextField(default='', null=True)),
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
                ('is_active', models.BooleanField(default=True, null=True)),
                ('is_deleted', models.BooleanField(default=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_governance_members', to='companies.company')),
                ('cover_image', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='governance_member_cover_image', to='medias.file')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='governance_member_former', to=settings.AUTH_USER_MODEL)),
                ('folder', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='medias.folder')),
                ('photo', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='governance_member_photo', to='medias.file')),
            ],
        ),
    ]
