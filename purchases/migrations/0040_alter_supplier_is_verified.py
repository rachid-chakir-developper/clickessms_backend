# Generated by Django 3.2.22 on 2025-01-15 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0039_supplier_is_verified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplier',
            name='is_verified',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
