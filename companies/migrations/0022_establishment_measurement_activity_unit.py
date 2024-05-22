# Generated by Django 3.2.22 on 2024-05-22 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0021_activityauthorization'),
    ]

    operations = [
        migrations.AddField(
            model_name='establishment',
            name='measurement_activity_unit',
            field=models.CharField(choices=[('DAY', 'Jour'), ('HOUR', 'Heure'), ('MONTH', 'Mois')], default='DAY', max_length=50),
        ),
    ]
