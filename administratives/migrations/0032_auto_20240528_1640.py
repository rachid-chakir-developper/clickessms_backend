# Generated by Django 3.2.22 on 2024-05-28 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('human_ressources', '0037_employeecontract_folder'),
        ('administratives', '0031_meeting_meeting_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='meetingdecision',
            name='against_voters',
            field=models.ManyToManyField(related_name='voted_against_decisions', to='human_ressources.Employee'),
        ),
        migrations.AddField(
            model_name='meetingdecision',
            name='for_voters',
            field=models.ManyToManyField(related_name='voted_for_decisions', to='human_ressources.Employee'),
        ),
    ]
