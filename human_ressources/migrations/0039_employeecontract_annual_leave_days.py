# Generated by Django 3.2.22 on 2024-06-20 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('human_ressources', '0038_auto_20240530_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeecontract',
            name='annual_leave_days',
            field=models.FloatField(default=25),
        ),
    ]
