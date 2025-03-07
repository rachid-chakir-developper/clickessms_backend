# Generated by Django 3.2.22 on 2024-11-28 14:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0020_expense_supplier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='supplier',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='supplier_expenses', to='purchases.supplier'),
        ),
    ]
