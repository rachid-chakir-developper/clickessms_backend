# Generated by Django 3.2.22 on 2024-01-30 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0002_auto_20231027_1003'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='is_active',
            field=models.BooleanField(default=True, null=True),
        ),
    ]
