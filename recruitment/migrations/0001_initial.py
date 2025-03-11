# Generated by Django 3.2.22 on 2025-03-06 11:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('companies', '0036_alter_establishment_measurement_activity_unit'),
        ('human_ressources', '0082_auto_20250227_1008'),
        ('medias', '0017_rename_measurement_activity_unit_documentrecord_notification_period_unit'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(editable=False, max_length=255, null=True)),
                ('title', models.CharField(max_length=255)),
                ('sector', models.CharField(max_length=255)),
                ('contract_type', models.CharField(choices=[('CDI', 'CDI'), ('CDD', 'CDD'), ('APPRENTICESHIP_CONTRACT', "Contrat d'apprentissage"), ('SINGLE_INTEGRATION_CONTRACT', "Contrat Unique d'Insertion (CUI)"), ('PROFESSIONALIZATION_CONTRACT', 'Contrat de professionnalisation'), ('SEASONAL_CONTRACT', 'Contrat saisonnier'), ('TEMPORARY_CONTRACT', 'Contrat intérimaire'), ('PART_TIME_CONTRACT', 'Contrat à temps partiel'), ('FULL_TIME_CONTRACT', 'Contrat à temps plein'), ('INTERNSHIP_CONTRACT', 'Contrat de stage')], default='CDI', max_length=50)),
                ('duration', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.TextField(default='', null=True)),
                ('observation', models.TextField(default='', null=True)),
                ('is_active', models.BooleanField(default=True, null=True)),
                ('is_deleted', models.BooleanField(default=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_job_positions', to='companies.company')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_job_positions', to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='job_positions', to='human_ressources.employee')),
                ('establishment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='job_positions', to='companies.establishment')),
                ('folder', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='medias.folder')),
            ],
        ),
        migrations.CreateModel(
            name='JobCandidate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(editable=False, max_length=255, null=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=20)),
                ('job', models.CharField(max_length=255)),
                ('availability', models.DateField(blank=True, null=True)),
                ('source', models.CharField(max_length=255)),
                ('description', models.TextField(default='', null=True)),
                ('observation', models.TextField(default='', null=True)),
                ('rating', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True, null=True)),
                ('is_deleted', models.BooleanField(default=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_job_candidates', to='companies.company')),
                ('cover_letter', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cover_letter_job_candidates', to='medias.file')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_job_candidates', to=settings.AUTH_USER_MODEL)),
                ('cv', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cv_job_candidates', to='medias.file')),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='job_candidates', to='human_ressources.employee')),
                ('folder', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='medias.folder')),
                ('interested_in', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='recruitment.jobposition')),
            ],
        ),
    ]
