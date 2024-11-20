# Generated by Django 3.2.22 on 2024-11-13 14:40

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0030_alter_company_status'),
        ('data_management', '0034_accountingnature'),
        ('human_ressources', '0057_employeecontractreplacedemployee_position'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('purchases', '0008_supplier_company'),
    ]

    operations = [
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(editable=False, max_length=255, null=True)),
                ('name', models.CharField(max_length=255, null=True)),
                ('total_amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('status', models.CharField(choices=[('DRAFT', 'Brouillon'), ('NEW', 'Nouveau'), ('PENDING', 'En Attente'), ('APPROVED', 'Approuvé'), ('REJECTED', 'Rejeté')], default='PENDING', max_length=20)),
                ('description', models.TextField(blank=True, default='', null=True)),
                ('observation', models.TextField(blank=True, default='', null=True)),
                ('is_active', models.BooleanField(default=True, null=True)),
                ('is_deleted', models.BooleanField(default=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_expenses', to='companies.company')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_expenses', to='human_ressources.employee')),
            ],
        ),
        migrations.CreateModel(
            name='ExpenseItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('description', models.TextField(blank=True, default='', null=True)),
                ('status', models.CharField(choices=[('PENDING', 'En Attente'), ('APPROVED', 'Approuvé'), ('REJECTED', 'Rejeté')], default='PENDING', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('accounting_nature', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expense_items', to='data_management.accountingnature')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('establishment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expense_items', to='companies.establishment')),
                ('expense', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expense_items', to='purchases.expense')),
            ],
        ),
    ]