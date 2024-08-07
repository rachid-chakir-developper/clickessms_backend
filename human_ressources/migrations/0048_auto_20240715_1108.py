# Generated by Django 3.2.22 on 2024-07-15 09:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0024_documenttype'),
        ('human_ressources', '0047_employee_social_security_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='gender',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='data_management.humangender'),
        ),
        migrations.AddField(
            model_name='employee',
            name='preferred_name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
