# Generated by Django 3.2.22 on 2024-02-01 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loan_management', '0005_alter_theobject_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='objectrecovery',
            name='number',
            field=models.CharField(editable=False, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='theobject',
            name='number',
            field=models.CharField(editable=False, max_length=255, null=True),
        ),
    ]
