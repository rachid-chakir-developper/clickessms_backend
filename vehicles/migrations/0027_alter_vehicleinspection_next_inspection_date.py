# Generated by Django 3.2.22 on 2024-06-03 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0026_alter_vehicleinspection_inspection_date_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicleinspection',
            name='next_inspection_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
