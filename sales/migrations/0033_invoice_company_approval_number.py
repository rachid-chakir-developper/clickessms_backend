# Generated by Django 3.2.22 on 2025-04-23 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0032_auto_20250423_1030'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='company_approval_number',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
