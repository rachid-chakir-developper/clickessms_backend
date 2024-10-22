# Generated by Django 3.2.22 on 2024-09-27 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0044_vehicleownership_rent_sale_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicleownership',
            name='ownership_type',
            field=models.CharField(choices=[('LEASE', 'Location Longue Durée'), ('LEASE_PURCHASE_OPTION', "Location avec option d'achat"), ('PURCHASE', 'Achat'), ('LOAN', 'Prêt'), ('SALE', 'Vendu')], default='LEASE', max_length=30, null=True),
        ),
    ]