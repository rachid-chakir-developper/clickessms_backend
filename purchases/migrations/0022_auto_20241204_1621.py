# Generated by Django 3.2.22 on 2024-12-04 15:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0033_auto_20241125_1105'),
        ('purchases', '0021_alter_expense_supplier'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='establishment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='establishment_expenses', to='companies.establishment'),
        ),
        migrations.DeleteModel(
            name='ExpenseEstablishment',
        ),
    ]
