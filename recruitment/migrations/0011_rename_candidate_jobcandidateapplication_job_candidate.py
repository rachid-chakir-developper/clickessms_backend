# Generated by Django 3.2.22 on 2025-03-12 10:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0010_auto_20250310_1530'),
    ]

    operations = [
        migrations.RenameField(
            model_name='jobcandidateapplication',
            old_name='candidate',
            new_name='job_candidate',
        ),
    ]
