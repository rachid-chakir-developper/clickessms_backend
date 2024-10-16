# Generated by Django 3.2.22 on 2024-10-08 14:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('human_ressources', '0052_auto_20241007_1022'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('companies', '0027_company_sce_shop_url'),
        ('data_management', '0024_documenttype'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255)),
                ('key', models.CharField(max_length=255, unique=True)),
                ('field_type', models.CharField(choices=[('TEXT', 'Text'), ('NUMBER', 'Number'), ('DATE', 'Date'), ('BOOLEAN', 'Boolean')], default='TEXT', max_length=50)),
                ('form_model', models.CharField(choices=[('Employee', 'Employé'), ('EmployeeContract', 'Contrat Employé')], max_length=50)),
                ('is_active', models.BooleanField(default=True, null=True)),
                ('is_deleted', models.BooleanField(default=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='custom_fields', to='companies.company')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='custom_fields', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CustomFieldValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(blank=True, null=True)),
                ('custom_field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_management.customfield')),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='custom_field_values', to='human_ressources.employee')),
                ('employee_contract', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='custom_field_values', to='human_ressources.employeecontract')),
            ],
        ),
    ]
