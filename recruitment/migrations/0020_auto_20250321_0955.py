# Generated by Django 3.2.22 on 2025-03-21 08:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0019_rename_message_jobcandidateinformationsheet_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobcandidateapplication',
            name='job_position',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='recruitment.jobposition'),
        ),
        migrations.AlterField(
            model_name='jobcandidateinformationsheet',
            name='job_position',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='recruitment.jobposition'),
        ),
    ]
