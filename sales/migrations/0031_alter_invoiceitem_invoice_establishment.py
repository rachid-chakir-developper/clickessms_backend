# Generated by Django 3.2.22 on 2025-04-01 06:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0030_auto_20250331_1150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceitem',
            name='invoice_establishment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invoice_items', to='sales.invoiceestablishment'),
        ),
    ]
