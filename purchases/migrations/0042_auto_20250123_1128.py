# Generated by Django 3.2.22 on 2025-01-23 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0041_expense_bank_card'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='bank_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='expense',
            name='check_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
