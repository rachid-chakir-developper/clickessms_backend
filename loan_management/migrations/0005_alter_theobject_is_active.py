# Generated by Django 3.2.22 on 2024-01-30 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loan_management', '0004_theobject_partner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='theobject',
            name='is_active',
            field=models.BooleanField(default=True, null=True),
        ),
    ]
