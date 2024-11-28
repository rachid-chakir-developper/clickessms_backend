# Generated by Django 3.2.22 on 2024-11-27 13:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0036_auto_20241126_1114'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('finance', '0032_budgetaccountingnature_amount_allocated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budgetaccountingnature',
            name='accounting_nature',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='budget_accounting_natures', to='data_management.accountingnature'),
        ),
        migrations.AlterField(
            model_name='budgetaccountingnature',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='budget_accounting_natures', to=settings.AUTH_USER_MODEL),
        ),
    ]