# Generated by Django 3.2.22 on 2024-05-31 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0021_auto_20240531_1232'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicleinspection',
            name='number',
            field=models.CharField(editable=False, max_length=255, null=True),
        ),
    ]
