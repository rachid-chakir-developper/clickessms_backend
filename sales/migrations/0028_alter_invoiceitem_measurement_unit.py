# Generated by Django 3.2.22 on 2025-02-27 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0027_auto_20250115_1417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceitem',
            name='measurement_unit',
            field=models.CharField(choices=[('HOUR', 'Heure'), ('DAY', 'Jour'), ('WEEK', 'Semaine'), ('MONTH', 'Mois')], default='DAY', max_length=50),
        ),
    ]
