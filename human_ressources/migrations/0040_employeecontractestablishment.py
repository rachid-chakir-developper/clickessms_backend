# Generated by Django 3.2.22 on 2024-06-21 09:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('companies', '0026_auto_20240530_1515'),
        ('human_ressources', '0039_employeecontract_annual_leave_days'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeContractEstablishment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_contract_establishment_former', to=settings.AUTH_USER_MODEL)),
                ('employee_contract', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='establishments', to='human_ressources.employeecontract')),
                ('establishment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_contract_establishment', to='companies.establishment')),
            ],
        ),
    ]