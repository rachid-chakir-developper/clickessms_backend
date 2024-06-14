# Generated by Django 3.2.22 on 2024-06-03 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0028_alter_vehicleinspection_next_inspection_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicleinspection',
            name='next_inspection_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehicleownership',
            name='purchase_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehicleownership',
            name='rental_ending_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehicleownership',
            name='rental_starting_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehicleownership',
            name='sale_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]