# Generated by Django 3.2.22 on 2025-03-10 14:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0036_alter_establishment_measurement_activity_unit'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('human_ressources', '0082_auto_20250227_1008'),
        ('data_management', '0049_jobplatform'),
        ('medias', '0017_rename_measurement_activity_unit_documentrecord_notification_period_unit'),
        ('recruitment', '0009_jobcandidate_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobcandidate',
            name='job_position',
        ),
        migrations.RemoveField(
            model_name='jobcandidate',
            name='status',
        ),
        migrations.CreateModel(
            name='JobCandidateApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(editable=False, max_length=255, null=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=20)),
                ('job_title', models.CharField(max_length=255)),
                ('availability_date', models.DateField(blank=True, null=True)),
                ('description', models.TextField(default='', null=True)),
                ('observation', models.TextField(default='', null=True)),
                ('rating', models.PositiveIntegerField(default=0)),
                ('status', models.CharField(choices=[('PENDING', 'En attente'), ('INTERESTED', 'Intéressant'), ('INTERVIEW', 'Entretien prévu'), ('OFFERED', 'Offre envoyée'), ('REJECTED', 'Rejeté'), ('ACCEPTED', 'Accepté')], default='PENDING', max_length=20)),
                ('is_active', models.BooleanField(default=True, null=True)),
                ('is_deleted', models.BooleanField(default=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('candidate', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='recruitment.jobcandidate')),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_job_candidate_applications', to='companies.company')),
                ('cover_letter', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cover_letter_job_candidate_applications', to='medias.file')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_candidate_applications', to=settings.AUTH_USER_MODEL)),
                ('cv', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cv_job_candidate_applications', to='medias.file')),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='job_candidate_applications', to='human_ressources.employee')),
                ('folder', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='medias.folder')),
                ('job_platform', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='data_management.jobplatform')),
                ('job_position', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='recruitment.jobposition')),
            ],
        ),
    ]
