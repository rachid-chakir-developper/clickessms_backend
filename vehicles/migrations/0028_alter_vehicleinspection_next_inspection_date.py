# Generated by Django 3.2.22 on 2024-06-03 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0027_alter_vehicleinspection_next_inspection_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicleinspection',
            name='next_inspection_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
