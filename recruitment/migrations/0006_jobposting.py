# Generated by Django 3.2.22 on 2025-03-07 15:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medias', '0017_rename_measurement_activity_unit_documentrecord_notification_period_unit'),
        ('companies', '0036_alter_establishment_measurement_activity_unit'),
        ('data_management', '0049_jobplatform'),
        ('human_ressources', '0082_auto_20250227_1008'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recruitment', '0005_jobposition_hiring_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobPosting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(editable=False, max_length=255, null=True)),
                ('title', models.CharField(max_length=255)),
                ('publication_date', models.DateField(auto_now_add=True)),
                ('expiration_date', models.DateField(blank=True, null=True)),
                ('is_published', models.BooleanField(default=False)),
                ('description', models.TextField(default='', null=True)),
                ('observation', models.TextField(default='', null=True)),
                ('is_deleted', models.BooleanField(default=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_job_postings', to='companies.company')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_job_postings', to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='job_postings', to='human_ressources.employee')),
                ('folder', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='medias.folder')),
                ('job_platforms', models.ManyToManyField(related_name='job_postings', to='data_management.JobPlatform')),
                ('job_position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_postings', to='recruitment.jobposition')),
            ],
        ),
    ]
