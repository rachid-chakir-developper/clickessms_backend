# Generated by Django 3.2.22 on 2025-03-12 11:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0011_rename_candidate_jobcandidateapplication_job_candidate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobcandidateapplication',
            name='job_candidate',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='job_candidate_applications', to='recruitment.jobcandidate'),
        ),
    ]
