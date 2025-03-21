# Generated by Django 3.2.22 on 2024-12-11 08:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('human_ressources', '0057_employeecontractreplacedemployee_position'),
        ('purchases', '0033_purchaseorder_validity_end_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorder',
            name='generator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='generated_purchase_orders', to='human_ressources.employee'),
        ),
    ]
