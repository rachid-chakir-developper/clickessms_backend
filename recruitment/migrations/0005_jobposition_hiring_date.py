# Generated by Django 3.2.22 on 2025-03-07 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0004_auto_20250306_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobposition',
            name='hiring_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
