# Generated by Django 3.2.22 on 2024-12-04 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0022_auto_20241204_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='expenseitem',
            name='quantity',
            field=models.FloatField(default=1, null=True),
        ),
    ]
