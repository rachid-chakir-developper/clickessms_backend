# Generated by Django 3.2.22 on 2025-02-27 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medias', '0015_documentrecord_beneficiary_document_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentrecord',
            name='measurement_activity_unit',
            field=models.CharField(choices=[('HOUR', 'Heure'), ('DAY', 'Jour'), ('WEEK', 'Semaine'), ('MONTH', 'Mois')], default='MONTH', max_length=50),
        ),
        migrations.AddField(
            model_name='documentrecord',
            name='notification_period_value',
            field=models.PositiveIntegerField(default=1, null=True),
        ),
    ]
