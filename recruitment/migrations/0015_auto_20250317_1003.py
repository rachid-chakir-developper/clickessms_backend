# Generated by Django 3.2.22 on 2025-03-17 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0014_jobcandidateinformationsheet'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobcandidateinformationsheet',
            name='cover_letter',
        ),
        migrations.RemoveField(
            model_name='jobcandidateinformationsheet',
            name='cv',
        ),
        migrations.AddField(
            model_name='jobcandidateinformationsheet',
            name='message',
            field=models.TextField(default='', null=True),
        ),
    ]
